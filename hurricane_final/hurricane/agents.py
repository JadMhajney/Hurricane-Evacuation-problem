#!/usr/bin/env python3
"""
FINAL CORRECTED agents.py - All issues fixed
"""
from typing import List, Tuple
from .world import TRAVERSE, EQUIP, UNEQUIP, NOOP, TERMINATE, World, AgentState
from .graph import Graph
from .search import SearchState, normalize_people, normalize_kits, greedy_one_step, a_star, rta_star, world_globals

def shortest_path_to_target(world: World, a: AgentState) -> List[Tuple[str, tuple]]:
    targets = [v for v,c in world.people.items() if c>0]
    if not targets:
        return []
    sp = world.graph.dijkstra(a.pos, amphib=a.equipped, P=world.P)
    reachable = [(sp[t][0], t) for t in targets if sp[t][0] < float('inf')]
    if not reachable:
        return []
    reachable.sort(key=lambda x: (x[0], x[1]))
    _, tgt = reachable[0]
    path = sp[tgt][1]
    actions = []
    for i in range(len(path)-1):
        u = path[i]; v = path[i+1]
        cand = []
        for _,e in world.graph.neighbors(u):
            if (e.u==u and e.v==v) or (e.u==v and e.v==u):
                cand.append(e.id)
        eid = min(cand)
        actions.append((TRAVERSE, (v, eid)))
    return actions

class HumanAgent:
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        print(f"\n{'='*60}")
        print(f"HUMAN AGENT {a.name} - YOUR TURN")
        print(f"Current position: V{a.pos}")
        print(f"Amphibian kit equipped: {'YES' if a.equipped else 'NO'}")
        print(f"People at current vertex: {world.people.get(a.pos, 0)}")
        print(f"\nAvailable actions:")
        print(f"  traverse <vertex> <edge_id>  - Move to adjacent vertex")
        print(f"  equip                        - Equip amphibian kit (if available)")
        print(f"  unequip                      - Unequip amphibian kit")
        print(f"  noop                         - Do nothing (1 time unit)")
        print(f"  terminate                    - End this agent's participation")
        
        print(f"\nAdjacent vertices:")
        for v, e in world.graph.neighbors(a.pos):
            flooded_str = " [FLOODED]" if e.flooded else ""
            can_traverse = world.can_traverse(a, e)
            status = "✓" if can_traverse else "✗"
            print(f"  {status} V{v} via Edge#{e.id} (weight={e.w}){flooded_str}")
        
        while True:
            try:
                cmd = input("\nEnter action: ").strip().lower().split()
                if not cmd:
                    continue
                    
                if cmd[0] == "traverse" and len(cmd) == 3:
                    to_v = int(cmd[1])
                    edge_id = int(cmd[2])
                    if edge_id not in world.graph.edges:
                        print(f"Error: Edge {edge_id} does not exist")
                        continue
                    return (TRAVERSE, (to_v, edge_id))
                    
                elif cmd[0] == "equip":
                    return (EQUIP, ())
                    
                elif cmd[0] == "unequip":
                    return (UNEQUIP, ())
                    
                elif cmd[0] == "noop":
                    return (NOOP, ())
                    
                elif cmd[0] == "terminate":
                    return (TERMINATE, ())
                    
                else:
                    print("Invalid command. Try again.")
                    
            except (ValueError, IndexError):
                print("Invalid input format. Try again.")

class StupidGreedyAgent:
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        if a.internal.get("terminated", False):
            return (TERMINATE, ())
        
        # Equip kit if at kit location and not equipped
        if not a.equipped and a.pos in world.kits:
            targets = [v for v, c in world.people.items() if c > 0]
            if targets:
                return (EQUIP, ())
        
        plan = a.internal.get("plan", [])
        current_target = a.internal.get("current_target", None)
        
        need_replan = False
        if not plan:
            need_replan = True
        elif current_target is not None and world.people.get(current_target, 0) == 0:
            need_replan = True
        
        if need_replan:
            plan = shortest_path_to_target(world, a)
            
            # If no path and not equipped, try to get kit first
            if not plan and not a.equipped and world.kits:
                sp = world.graph.dijkstra(a.pos, amphib=False, P=world.P)
                reachable_kits = [(sp[k][0], k) for k in world.kits if sp[k][0] < float('inf')]
                if reachable_kits:
                    reachable_kits.sort(key=lambda x: (x[0], x[1]))
                    _, kit_pos = reachable_kits[0]
                    path = sp[kit_pos][1]
                    plan = []
                    for i in range(len(path)-1):
                        u = path[i]; v = path[i+1]
                        cand = []
                        for _,e in world.graph.neighbors(u):
                            if (e.u==u and e.v==v) or (e.u==v and e.v==u):
                                cand.append(e.id)
                        eid = min(cand)
                        plan.append((TRAVERSE, (v, eid)))
                    if plan:
                        a.internal["going_for_kit"] = True
            
            a.internal["plan"] = plan
            if plan and not a.internal.get("going_for_kit", False):
                for act in reversed(plan):
                    if act[0] == TRAVERSE:
                        a.internal["current_target"] = act[1][0]
                        break
            else:
                a.internal["current_target"] = None
        
        if not plan:
            a.internal["terminated"] = True
            return (TERMINATE, ())
        
        action = plan.pop(0)
        a.internal["plan"] = plan
        
        if a.internal.get("going_for_kit", False) and not plan:
            a.internal["going_for_kit"] = False
        
        return action

class ThiefAgent:
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        if not a.equipped:
            if a.pos in world.kits:
                return (EQUIP, ())
            kits = list(world.kits)
            if not kits:
                return (NOOP, ())
            sp = world.graph.dijkstra(a.pos, amphib=False, P=world.P)
            reachable = [(sp[k][0], k) for k in kits if sp[k][0] < float('inf')]
            if not reachable:
                return (NOOP, ())
            reachable.sort(key=lambda x:(x[0], x[1]))
            _, tgt = reachable[0]
            path = sp[tgt][1]
            if len(path) <= 1:
                return (NOOP, ())
            u = path[0]; v = path[1]
            cand = []
            for _,e in world.graph.neighbors(u):
                if (e.u==u and e.v==v) or (e.u==v and e.v==u):
                    cand.append(e.id)
            eid = min(cand)
            return (TRAVERSE, (v, eid))
        
        other_positions = a.internal.get("others", [])
        if not other_positions:
            return (NOOP, ())
        
        best = None
        best_score = -1
        
        for v, e in world.graph.neighbors(a.pos):
            if not world.can_traverse(a, e):
                continue
            
            score = 0
            sp_from_v = world.graph.dijkstra(v, amphib=True, P=world.P)
            for other_pos in other_positions:
                d = sp_from_v[other_pos][0]
                if d == float('inf'):
                    d = 1e9
                score += d
            
            if score > best_score or (score == best_score and (best is None or v < best)):
                best_score = score
                best = v
        
        if best is None:
            return (NOOP, ())
        
        cand = []
        for _, e in world.graph.neighbors(a.pos):
            vv = e.v if e.u == a.pos else e.u
            if vv == best:
                cand.append(e.id)
        eid = min(cand)
        return (TRAVERSE, (best, eid))

def _make_search_state(world: World, a: AgentState) -> SearchState:
    people = dict(world.people)
    if a.pos in people:
        people[a.pos] = 0
    return SearchState(a.pos, a.equipped, normalize_people(people), normalize_kits(world.kits))

class GreedySearchAgent:
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        if a.internal.get("terminated", False):
            return (TERMINATE, ())
        
        # Greedy Search Agent (Local 1-step lookahead)
        # Does NOT plan ahead. Always re-evaluates.
        
        s0 = _make_search_state(world, a)
        world_globals["Q"] = world.Q
        world_globals["U"] = world.U
        
        # Always 1 expansion per move
        plan, expansions = greedy_one_step(world.graph, world.P, s0)
        world.time += expansions * a.internal.get("T", 0.0)
        
        if not plan:
            a.internal["terminated"] = True
            return (TERMINATE, ())
            
        return plan[0]

class AStarAgent:
    def __init__(self, LIMIT: int = 10000):
        self.LIMIT = LIMIT
    
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        if a.internal.get("terminated", False):
            return (TERMINATE, ())
        
        plan = a.internal.get("plan", [])
        
        if not plan:
            s0 = _make_search_state(world, a)
            world_globals["Q"] = world.Q
            world_globals["U"] = world.U
            plan, expansions = a_star(world.graph, world.P, s0, LIMIT=self.LIMIT)
            world.time += expansions * a.internal.get("T", 0.0)
            
            if not plan:
                a.internal["terminated"] = True
                return (TERMINATE, ())
            
            a.internal["plan"] = plan[:]
        
        if not a.internal["plan"]:
            a.internal["terminated"] = True
            return (TERMINATE, ())
        
        action = a.internal["plan"].pop(0)
        return action

class RealTimeAStarAgent:
    def __init__(self, L: int = 10):
        self.L = L
    
    def __call__(self, world: World, a: AgentState) -> Tuple[str, tuple]:
        if a.internal.get("terminated", False):
            return (TERMINATE, ())
        
        # Check if no more targets
        remaining = [v for v, c in world.people.items() if c > 0]
        if not remaining:
            a.internal["terminated"] = True
            return (TERMINATE, ())
        
        # CRITICAL FIX: Limit total actions to prevent infinite loops
        total_actions = a.internal.get("rta_action_count", 0)
        if total_actions > 1000:  # Hard limit
            a.internal["terminated"] = True
            return (TERMINATE, ())
        
        s0 = _make_search_state(world, a)
        world_globals["Q"] = world.Q
        world_globals["U"] = world.U
        plan, expansions = rta_star(world.graph, world.P, s0, L=self.L)
        world.time += expansions * a.internal.get("T", 0.0)
        
        if not plan:
            a.internal["terminated"] = True
            return (TERMINATE, ())
        
        a.internal["rta_action_count"] = total_actions + 1
        action = plan[0]
        return action