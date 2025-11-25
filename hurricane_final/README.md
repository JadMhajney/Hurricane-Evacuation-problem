# Hurricane Evacuation Problem — Simulator & Agents (Final)

Implements:
- Flooded edges & amphibian kits (equip Q, unequip U, equipped traversal multiplies cost by P on all edges; flooded edges require kit).
- Agents: human, stupid_greedy, thief, greedy_search, astar(--limit), rta(--L).
- Heuristic (admissible): h = min(dist(current, any target)) + MST(remaining targets) under current amphibious capability.
- Situated planning time T: expansions*T added to world time (Greedy per plan; A* once when planned; RT-A* each decision).

Run:
```bash
python -m hurricane.run --input hurricane/examples/small.txt   --agents stupid_greedy thief astar   --starts 1 1 3 --limit 10000 --L 10 --T 0.01
```
