#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import heapq, math

@dataclass
class Edge:
    u: int
    v: int
    w: int
    flooded: bool
    id: int

@dataclass
class Graph:
    n: int
    edges: Dict[int, Edge] = field(default_factory=dict)
    adj: Dict[int, List[int]] = field(default_factory=dict)  # vertex -> list of edge ids

    def add_edge(self, eid: int, u: int, v: int, w: int, flooded: bool):
        self.edges[eid] = Edge(u, v, w, flooded, eid)
        self.adj.setdefault(u, []).append(eid)
        self.adj.setdefault(v, []).append(eid)

    def neighbors(self, u: int):
        for eid in sorted(self.adj.get(u, [])):
            e = self.edges[eid]
            v = e.v if e.u == u else e.u
            yield v, e

    def dijkstra(self, start: int, amphib: bool, P: int) -> Dict[int, Tuple[float, List[int]]]:
        """Return dist and path (as vertices)."""
        dist = {v: math.inf for v in range(1, self.n+1)}
        prev = {v: None for v in range(1, self.n+1)}
        dist[start] = 0.0
        pq = [(0.0, start)]
        while pq:
            d,u = heapq.heappop(pq)
            if d != dist[u]: 
                continue
            for v,e in self.neighbors(u):
                if (not amphib) and e.flooded:
                    continue
                cost = e.w * (P if amphib else 1)
                nd = d + cost
                if nd < dist[v] or (nd == dist[v] and v < u):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        paths = {}
        for t in range(1, self.n+1):
            if dist[t] == math.inf:
                paths[t] = (math.inf, [])
            else:
                path = []
                cur = t
                while cur is not None:
                    path.append(cur)
                    cur = prev[cur]
                path.reverse()
                paths[t] = (dist[t], path)
        return paths
