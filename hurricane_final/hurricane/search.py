#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Tuple, List, Dict, Set
from .world import TRAVERSE, EQUIP, UNEQUIP, NOOP, TERMINATE
from .graph import Graph
from .heuristic import admissible_heuristic
import heapq, math
from itertools import count

@dataclass(frozen=True)
class SearchState:
    pos: int
    equipped: bool
    people: frozenset   # of (vertex,count>0)
    kits: frozenset     # of vertex ids

    def targets(self) -> List[int]:
        return [v for v,c in self.people if c > 0]

def normalize_people(d: Dict[int,int]) -> frozenset:
    return frozenset((v,c) for v,c in d.items() if c>0)

def normalize_kits(s: Set[int]) -> frozenset:
    return frozenset(sorted(s))

def successors(graph: Graph, P: int, state: SearchState) -> List[Tuple[float, Tuple[str, tuple], SearchState]]:
    pos = state.pos
    amph = state.equipped
    res = []

    if (not amph) and (pos in state.kits):
        newkits = set(state.kits); newkits.remove(pos)
        res.append((world_globals["Q"], (EQUIP, ()), SearchState(pos, True, state.people, normalize_kits(newkits))))

    if amph:
        newkits = set(state.kits); newkits.add(pos)
        res.append((world_globals["U"], (UNEQUIP, ()), SearchState(pos, False, state.people, normalize_kits(newkits))))

    for v,e in graph.neighbors(pos):
        if (not amph) and e.flooded:
            continue
        cost = e.w * (P if amph else 1)
        newp = {vv: cc for vv,cc in state.people}
        if newp.get(v, 0) > 0:
            newp[v] = 0
        ns = SearchState(v, amph, normalize_people(newp), state.kits)
        res.append((cost, (TRAVERSE, (v, e.id)), ns))

    res.append((1.0, (NOOP, ()), SearchState(pos, amph, state.people, state.kits)))
    return res

world_globals = {"Q": 0, "U": 0}

def greedy_one_step(graph: Graph, P: int, start: SearchState):
    """
    Local Greedy Search (1-step lookahead):
    1. Generate all immediate successors.
    2. Evaluate h(successor) for each.
    3. Pick the action leading to the successor with the lowest h.
    4. Break ties by preferring lower vertex IDs.
    Returns: ([action], expansions=1)
    """
    # Trivial goal test
    if len(start.targets()) == 0:
        return [], 0
        
    candidates = []
    for cost, action, ns in successors(graph, P, start):
        # Ignore NOOP in greedy search (prevents infinite loops when stuck)
        if action[0] == NOOP:
            continue
            
        h = admissible_heuristic(graph, ns.pos, ns.targets(), ns.equipped, P)
        candidates.append((h, action))
        
    if not candidates:
        return [], 1
        
    # Tie-break: min h, then min vertex ID in action params
    def tiebreaker(item):
        h_val, act = item
        kind, params = act
        # Prefer moves that progress to lower to_v as a mild, stable tiebreak
        v_id = 10**9
        if kind == TRAVERSE and isinstance(params, tuple) and len(params) >= 1:
            v_id = params[0]
        return (h_val, v_id)
        
    best_h, best_action = min(candidates, key=tiebreaker)
    
    # If best_h is infinite, we are stuck
    if best_h == float('inf'):
        return [], 1
        
    return [best_action], 1

def a_star(graph: Graph, P: int, start: SearchState, LIMIT: int = 10000):
    cnt = 0
    frontier = []
    gscore = {start: 0.0}
    parent = {start: (None, None)}
    tie = count()
    f0 = admissible_heuristic(graph, start.pos, start.targets(), start.equipped, P)
    heapq.heappush(frontier, (f0, next(tie), 0.0, start))
    expanded = set()
    while frontier:
        f, _, g, s = heapq.heappop(frontier)
        if s in expanded:
            continue
        expanded.add(s)
        cnt += 1
        if cnt > LIMIT:
            return [], cnt
        if len(s.targets()) == 0:
            path = []
            cur = s
            while parent[cur][0] is not None:
                prev, action = parent[cur]
                path.append(action)
                cur = prev
            path.reverse()
            return path, cnt
        for cost, action, ns in successors(graph, P, s):
            ng = g + cost
            if ng < gscore.get(ns, math.inf):
                gscore[ns] = ng
                parent[ns] = (s, action)
                h = admissible_heuristic(graph, ns.pos, ns.targets(), ns.equipped, P)
                heapq.heappush(frontier, (ng + h, next(tie), ng, ns))
    return [], cnt

def rta_star(graph: Graph, P: int, start: SearchState, L: int = 10):
    """
    Real-Time A* (RT-A*):
      - Search up to L expansions starting from `start`.
      - For every IMMEDIATE successor action of `start`, track the BEST f = g + h
        encountered along any path within the depth-limited search that BEGINS with that action.
      - If a goal is found within the lookahead, return the full plan to it.
      - Otherwise, execute the immediate action whose best f is minimal (ties -> smaller vertex id).
    Returns: (plan, expansions) where `plan` is either a full plan to goal or a single action.
    """
    # Trivial goal test first
    if len(start.targets()) == 0:
        return [], 0

    # Priority queue entries: (f, tie, g, state, first_action)
    tie = count()
    expansions = 0
    expanded: Set[SearchState] = set()
    parent: Dict[SearchState, Tuple[SearchState, Tuple[str, tuple]]] = {start: (None, None)}

    # Seed frontier from IMMEDIATE successors so we can label each path with its first action
    frontier = []
    best_f_by_action: Dict[Tuple[str, tuple], float] = {}

    for cost, action, ns in successors(graph, P, start):
        g0 = cost
        h0 = admissible_heuristic(graph, ns.pos, ns.targets(), ns.equipped, P)
        f0 = g0 + h0
        best_f_by_action[action] = f0
        if ns != start:
            parent[ns] = (start, action)
        heapq.heappush(frontier, (f0, next(tie), g0, ns, action))

    goal_state = None

    while frontier and expansions < L:
        f, _, g, s, first_action = heapq.heappop(frontier)
        if s in expanded:
            continue
        expanded.add(s)
        expansions += 1

        # Update best seen f for this first_action
        if f < best_f_by_action.get(first_action, float("inf")):
            best_f_by_action[first_action] = f

        # Goal?
        if len(s.targets()) == 0:
            goal_state = s
            break

        # Expand successors
        for cost, action, ns in successors(graph, P, s):
            ng = g + cost
            h = admissible_heuristic(graph, ns.pos, ns.targets(), ns.equipped, P)
            nf = ng + h
            if ns not in expanded:
                # Preserve the first action that led away from the root
                if ns != s:
                    parent[ns] = (s, action)
                heapq.heappush(frontier, (nf, next(tie), ng, ns, first_action))

    # If we found a goal within the lookahead, return full plan to it
    if goal_state is not None:
        plan = []
        cur = goal_state
        iterations = 0
        max_iterations = 100  # Safety limit
        while parent[cur][0] is not None and iterations < max_iterations:
            iterations += 1
            prev, action = parent[cur]
            plan.append(action)
            cur = prev
        plan.reverse()
        if iterations >= max_iterations:
            return [], expansions 
        return plan, expansions

    # Otherwise choose the immediate action whose best f was minimal
    if not best_f_by_action:
        # No legal moves (dead end)
        return [], expansions

    # Check if all f-values are infinite (no path to goal exists)
    best_f = min(best_f_by_action.values())
    if best_f == float('inf') or best_f >= 1e9:
        # All paths lead nowhere - terminate
        return [], expansions

    if len(best_f_by_action) == 1 and list(best_f_by_action.keys())[0][0] == NOOP:
    # Only NOOP available and it doesn't lead to goal
        return [], expansions

    # Tie-break by lexical/min id via action's parameter if equal f
    # (Actions are tuples like (TRAVERSE, (to_v, eid)) or (EQUIP, ()), etc.)
    def action_tiebreak(a):
        kind, params = a
        # Prefer moves that progress to lower to_v as a mild, stable tiebreak
        if kind == TRAVERSE and isinstance(params, tuple) and len(params) >= 1:
            return params[0]
        return 10**9  # neutral fallback

    candidates = [a for a, f in best_f_by_action.items() if f == best_f]
    chosen = sorted(candidates, key=action_tiebreak)[0]
    return [chosen], expansions