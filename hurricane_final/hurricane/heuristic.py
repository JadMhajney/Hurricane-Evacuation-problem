#!/usr/bin/env python3
from typing import Dict, List, Tuple
from .graph import Graph
import heapq, math

#!/usr/bin/env python3
"""
ADMISSIBLE HEURISTIC FOR HURRICANE EVACUATION PROBLEM

Rationale and Proof of Admissibility:
=====================================

Our heuristic function h(state) estimates the minimum time remaining to rescue
all people from the current state. It is defined as:

    h(state) = min_distance_to_any_target + MST_cost(remaining_targets)

Where both components use an OPTIMISTIC distance metric.

1. OPTIMISTIC DISTANCE METRIC:
   - For each edge with weight w and flooded status f:
     * Real cost with kit: w * P
     * Real cost without kit: w (if not flooded), infinity (if flooded)
     * Optimistic cost: min(w, w*P) regardless of flooded status
   
   - We IGNORE equip time Q and unequip time U in the heuristic
   
   This is a LOWER BOUND because:
   a) We assume we can traverse ANY edge (even flooded ones without a kit)
   b) We take the minimum possible traversal cost on each edge
   c) We ignore time costs for equipping/unequipping

2. FIRST COMPONENT - Distance to Closest Target:
   min_distance_to_any_target = min over all targets t of optimistic_dist(current, t)
   
   This is admissible because:
   - We MUST visit at least one target next
   - The optimistic distance is ≤ any actual path cost to that target
   - Therefore, this is a lower bound on the next step

3. SECOND COMPONENT - MST of Remaining Targets:
   We compute a Minimum Spanning Tree over all remaining target vertices
   using the optimistic pairwise distances.
   
   This is admissible because:
   - After reaching the first target, we must visit all others
   - An MST provides a lower bound on the cost to connect all vertices
   - The actual tour must be at least as long as the MST
   - Using optimistic distances makes this an even stronger lower bound

4. COMBINED ADMISSIBILITY:
   h(state) = component_1 + component_2 is admissible because:
   - The actual cost is at least: (cost to reach first target) + (cost to visit rest)
   - Component_1 ≤ (cost to reach first target)
   - Component_2 ≤ (cost to visit rest)
   - Therefore h(state) ≤ optimal_cost(state)

5. WHY THIS HEURISTIC IS EFFECTIVE:
   - It's much better than "distance to farthest target" (not admissible)
   - It's much better than "0" (trivially admissible but useless)
   - The MST component captures the "spread" of remaining targets
   - It provides good guidance in A* search without overestimating

THEORETICAL COMPLEXITY:
- Computing optimistic Dijkstra from one vertex: O(E log V)
- Computing MST for k targets: O(k²)
- Total heuristic evaluation: O(E log V) per call in worst case
- In practice, we can cache distance computations for efficiency
"""

from typing import Dict, List, Tuple
from .graph import Graph
import heapq, math

def _optimistic_dists(graph: Graph, P: int, start: int) -> Dict[int, float]:
    """
    Optimistic single-source shortest paths:
      - All edges are traversable.
      - Edge cost = min(w, w*P). (Ignore equip/unequip times.)
    This is a LOWER BOUND on true travel time from 'start'.
    """
    dist = {v: math.inf for v in range(1, graph.n + 1)}
    dist[start] = 0.0
    pq: List[Tuple[float, int]] = [(0.0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, e in graph.neighbors(u):
            cost = min(e.w, e.w * P)   # optimistic lower bound per edge
            nd = d + cost
            if nd < dist[v] or (nd == dist[v] and v < u):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

def _pairwise_optimistic(graph: Graph, P: int, nodes: List[int]) -> Dict[int, Dict[int, float]]:
    """
    For each node in 'nodes', compute optimistic distances to all vertices,
    then read off pairwise distances between nodes.
    """
    table: Dict[int, Dict[int, float]] = {}
    for s in nodes:
        d = _optimistic_dists(graph, P, s)
        table[s] = {t: d[t] for t in range(1, graph.n + 1)}
    return table

def _mst_cost(nodes: List[int], dist: Dict[int, Dict[int, float]]) -> float:
    if not nodes:
        return 0.0
    seen = {nodes[0]}
    total = 0.0
    pq: List[Tuple[float, int, int]] = []
    # initialize with edges from the root
    for v in nodes[1:]:
        heapq.heappush(pq, (dist[nodes[0]][v], nodes[0], v))
    while len(seen) < len(nodes) and pq:
        w, u, v = heapq.heappop(pq)
        if v in seen:
            continue
        seen.add(v)
        total += w
        for x in nodes:
            if x not in seen:
                heapq.heappush(pq, (dist[v][x], v, x))
    return total

_dist_cache = {}

def clear_heuristic_cache():
    """Clear the distance cache - useful between different problem instances"""
    global _dist_cache
    _dist_cache = {}

def admissible_heuristic(graph: Graph, cur: int, targets: List[int], amphib: bool, P: int) -> float:
    """
    Admissible heuristic:
      h = optimistic distance from 'cur' to the closest target
          + MST over remaining targets,
      where distances are computed under the optimistic metric:
        - flooded edges allowed
        - edge cost = min(w, w*P)
        - no Q/U times
    """
    if not targets:
        return 0.0

    # optimistic distance from current to each target
    cache_key = (graph.n, P, cur)
    if cache_key not in _dist_cache:
        _dist_cache[cache_key] = _optimistic_dists(graph, P, cur)
    dcur = _dist_cache[cache_key]
    to_any = min(dcur[t] for t in targets)

    # optimistic pairwise distances among targets, then MST
    inner = {t: {} for t in targets}
    for t in targets:
        dt = _optimistic_dists(graph, P, t)
        for u in targets:
            inner[t][u] = dt[u]

    mcost = _mst_cost(targets, inner)
    return to_any + mcost
