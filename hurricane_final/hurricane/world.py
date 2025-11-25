#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set
from .graph import Graph, Edge

TRAVERSE = "traverse"  # params: (to_vertex, edge_id)
EQUIP = "equip"
UNEQUIP = "unequip"
NOOP = "no-op"
TERMINATE = "terminate"

@dataclass
class AgentState:
    name: str
    agent_type: str
    pos: int
    equipped: bool = False
    actions: int = 0
    saved: int = 0
    score: float = 0.0
    internal: dict = field(default_factory=dict)

@dataclass
class World:
    graph: Graph
    Q: int
    U: int
    P: int
    people: Dict[int, int]
    kits: Set[int]
    time: float = 0.0

    def total_people(self) -> int:
        return sum(self.people.values())

    def all_saved(self) -> bool:
        return self.total_people() == 0

    def can_traverse(self, a: AgentState, edge: Edge) -> bool:
        return (not edge.flooded) or a.equipped

    def pick_up_people(self, a: AgentState):
        if a.agent_type == "thief":
            return 0
        count = self.people.get(a.pos, 0)
        if count > 0:
            a.saved += count
            self.people[a.pos] = 0
            return count
        return 0

    def do_action(self, a: AgentState, action: Tuple[str, tuple]):
        kind, params = action
        a.actions += 1
        if kind == TERMINATE:
            return
        if kind == NOOP:
            self.time += 1
            return
        if kind == EQUIP:
            if (a.pos in self.kits) and (not a.equipped):
                self.kits.remove(a.pos)
                self.time += self.Q
                a.equipped = True
            else:
                self.time += 1
            return
        if kind == UNEQUIP:
            if a.equipped:
                self.time += self.U
                a.equipped = False
                self.kits.add(a.pos)
            else:
                self.time += 1
            return
        if kind == TRAVERSE:
            to_v, edge_id = params
            e = self.graph.edges[edge_id]
            if self.can_traverse(a, e):
                cost = e.w * (self.P if a.equipped else 1)
                self.time += cost
                a.pos = to_v
            else:
                self.time += 1
            return
        raise ValueError(f"Unknown action {kind}")

    def recompute_scores(self, agents: List['AgentState']):
        for a in agents:
            a.score = a.saved * 1000 - self.time

def parse_world_from_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith(";")]

    n = None; Q=None; U=None; P=None
    people = {}
    kits = set()
    edges = []
    for ln in lines:
        if ln.startswith("#N"):
            n = int(ln.split()[1])
        elif ln.startswith("#U"):
            U = int(ln.split()[1])
        elif ln.startswith("#Q"):
            Q = int(ln.split()[1])
        elif ln.startswith("#P"):
            P = int(ln.split()[1])
        elif ln.startswith("#V"):
            parts = ln[2:].split()
            vid = int(parts[0])
            contents = parts[1:]
            ppl = 0; has_k=False
            for c in contents:
                if c.startswith("P"):
                    ppl += int(c[1:])
                elif c == "K":
                    has_k = True
            if ppl > 0:
                people[vid] = ppl
            if has_k:
                kits.add(vid)
        elif ln.startswith("#E"):
            parts = ln.split()
            eid = int(parts[0][2:])
            u = int(parts[1]); v = int(parts[2])
            w = int(parts[3][1:])
            flooded = ("F" in parts[4:])
            edges.append((eid, u, v, w, flooded))

    assert None not in (n,Q,U,P), "Missing globals (#N,#U,#Q,#P)"
    from .graph import Graph
    g = Graph(n=n)
    for eid,u,v,w,f in edges:
        g.add_edge(eid,u,v,w,f)

    world = World(graph=g, Q=Q, U=U, P=P, people=people, kits=kits, time=0.0)
    return world, {"N": n, "Q": Q, "U": U, "P": P}
