#!/usr/bin/env python3
import argparse
from typing import List
from .world import World, AgentState, parse_world_from_file, TRAVERSE, EQUIP, UNEQUIP, NOOP, TERMINATE
from .agents import HumanAgent, StupidGreedyAgent, ThiefAgent, GreedySearchAgent, AStarAgent, RealTimeAStarAgent

AGENT_TYPES = {
    "human": HumanAgent,
    "stupid_greedy": StupidGreedyAgent,
    "thief": ThiefAgent,
    "greedy_search": GreedySearchAgent,
    "astar": AStarAgent,
    "rta": RealTimeAStarAgent,
}

def can_any_agent_reach_targets(world: World, agents: List[AgentState]) -> bool:
    """Check if any agent can reach any remaining target."""
    targets = [v for v, c in world.people.items() if c > 0]
    if not targets:
        return False
    
    for a in agents:
        if a.agent_type == "thief":
            continue
        sp = world.graph.dijkstra(a.pos, amphib=a.equipped, P=world.P)
        for t in targets:
            if sp[t][0] < float('inf'):
                return True
        
        # Check if agent can equip a kit and reach targets
        if not a.equipped:
            for kit_v in world.kits:
                if sp[kit_v][0] < float('inf'):
                    sp_with_kit = world.graph.dijkstra(kit_v, amphib=True, P=world.P)
                    for t in targets:
                        if sp_with_kit[t][0] < float('inf'):
                            return True
    return False

def fmt_world(world: World, agents: List[AgentState]) -> str:
    lines = []
    lines.append("=== WORLD STATE ===")
    for a in agents:
        term_marker = " [TERMINATED]" if a.internal.get("terminated", False) else ""
        lines.append(f"Agent {a.name:>2} [{a.agent_type}] @V{a.pos} kit={'Y' if a.equipped else 'N'} | time={world.time:.3f} actions={a.actions} saved={a.saved} score={a.score:.2f}{term_marker}")
    lines.append("People per vertex:")
    parts = []
    for v in range(1, world.graph.n+1):
        parts.append(f"   V{v}:{world.people.get(v,0)}")
    lines.append(" ".join(parts))
    lines.append("Kits at: " + (" ".join(f"V{v}" for v in sorted(world.kits)) if world.kits else "(none)"))
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description="Hurricane Evacuation Problem simulator")
    ap.add_argument("--input", required=True, help="Path to graph file (ASCII format)")
    ap.add_argument("--agents", nargs="+", required=False, default=["stupid_greedy","thief","astar"], help="List of agent types")
    ap.add_argument("--starts", nargs="+", required=False, default=["1","1","1"], help="Starting vertices for each agent (1-indexed)")
    ap.add_argument("--limit", type=int, default=10000, help="A* expansion limit")
    ap.add_argument("--L", type=int, default=10, help="RTA* expansions per decision")
    ap.add_argument("--T", type=float, default=0.0, help="Per-expansion time (situated planning)")
    args = ap.parse_args()

    world, g = parse_world_from_file(args.input)

    agents = []
    policies = []
    for i, kind in enumerate(args.agents):
        if kind not in AGENT_TYPES:
            raise SystemExit(f"Unknown agent type: {kind}")
        if kind == "astar":
            inst = AGENT_TYPES[kind](LIMIT=args.limit)
        elif kind == "rta":
            inst = AGENT_TYPES[kind](L=args.L)
        else:
            inst = AGENT_TYPES[kind]()
        pos = int(args.starts[i]) if i < len(args.starts) else 1
        astate = AgentState(name=f"A{i+1}", agent_type=kind, pos=pos, internal={"others": [], "terminated": False})
        astate.internal["T"] = args.T
        agents.append(astate)
        policies.append(inst)

    for i,a in enumerate(agents):
        others = [b.pos for j,b in enumerate(agents) if j!=i]
        a.internal["others"] = others

    # Pick up people at initial positions
    for a in agents:
        world.pick_up_people(a)

    step = 0
    world.recompute_scores(agents)
    print(fmt_world(world, agents))

    MAX_STEPS = 100000
    idle_rounds = 0
    consecutive_no_progress = 0
    termination_reason = None  # Track why simulation ended
    
    while step < MAX_STEPS:
        progressed = False
        any_action_taken = False
        
        for i,a in enumerate(agents):
            # Skip if already terminated
            if a.internal.get("terminated", False):
                continue
            
            # Check if already done
            if world.all_saved():
                break
            
            # Get action from agent
            action = policies[i].__call__(world, a)
            
            # Handle termination
            if action[0] == TERMINATE:
                a.internal["terminated"] = True
                continue
            
            any_action_taken = True
            
            # Track if this is a move action
            old_pos = a.pos
            
            # Execute action
            world.do_action(a, action)
            
            # Pick up people if agent moved to new location
            before = sum(world.people.values())
            if action[0] == TRAVERSE and a.pos != old_pos:
                world.pick_up_people(a)
            after = sum(world.people.values())
            if after < before:
                progressed = True
            
            # Update ALL agents' knowledge of other positions
            for j, b in enumerate(agents):
                b.internal["others"] = [c.pos for idx, c in enumerate(agents) if idx != j]
            
            progressed = progressed or (action[0] not in [NOOP, TERMINATE])
            world.recompute_scores(agents)
            print(fmt_world(world, agents))
            
            if world.all_saved():
                break
        
        step += 1
        
        # Check if all people rescued
        if world.all_saved():
            termination_reason = "SUCCESS: All people rescued"
            print(f"\n{'='*60}")
            print(f"  {termination_reason}")
            print(f"{'='*60}")
            break
        
        # Check if all non-thief agents have terminated
        non_thief_agents = [a for a in agents if a.agent_type != "thief"]
        all_terminated = all(a.internal.get("terminated", False) for a in non_thief_agents)
        
        if all_terminated:
            termination_reason = "NATURAL: All agents terminated (no valid paths)"
            print(f"\n{'='*60}")
            print(f"  {termination_reason}")
            print(f"{'='*60}")
            break
        
        # Track consecutive rounds with no progress
        if not progressed:
            consecutive_no_progress += 1
        else:
            consecutive_no_progress = 0
        
        # Emergency brake: if no progress for 20 consecutive rounds, force terminate all
        if consecutive_no_progress >= 20:
            termination_reason = "⚠️  FORCED: Emergency brake (no progress for 20 rounds)"
            print(f"\n{'='*60}")
            print(f"  {termination_reason}")
            print(f"  This indicates agents were stuck in infinite loop!")
            print(f"{'='*60}")
            for a in non_thief_agents:
                a.internal["terminated"] = True
                a.internal["forced_termination"] = True
            break
        
        # Check for idle rounds
        if not any_action_taken:
            idle_rounds += 1
            if idle_rounds > 5:
                if not can_any_agent_reach_targets(world, agents):
                    termination_reason = "NATURAL: No path exists to remaining targets"
                    print(f"\n{'='*60}")
                    print(f"  {termination_reason}")
                    print(f"{'='*60}")
                    break
                else:
                    termination_reason = "TIMEOUT: No actions taken for 5+ rounds"
                    print(f"\n{'='*60}")
                    print(f"  {termination_reason}")
                    print(f"{'='*60}")
                    break
        else:
            idle_rounds = 0

    world.recompute_scores(agents)
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    # Show termination reason
    if termination_reason:
        print(f"Termination Reason: {termination_reason}")
        # Mark agents with forced termination
        forced_agents = [a.name for a in agents if a.internal.get("forced_termination", False)]
        if forced_agents:
            print(f"⚠️  Agents force-stopped: {', '.join(forced_agents)}")
        print("-" * 60)
    
    print(f"Total simulation time: {world.time:.3f}")
    print(f"Total steps executed: {step}")
    total_saved = sum(a.saved for a in agents)
    print(f"Total saved={total_saved}\n")
    print(f"{'Agent':<8} {'Type':<15} {'Saved':>5} {'Actions':>8} {'Score':>10}")

    print("-" * 50)
    for a in agents:
        forced_marker = " ⚠️ FORCED" if a.internal.get("forced_termination", False) else ""
        print(f"{a.name:<8} {a.agent_type:<15} {a.saved:>5} {a.actions:>8} {a.score:>10.2f}{forced_marker}")
    print("-" * 50)
    
    # Find winner (only among rescue agents, not thieves)
    rescue_agents = [a for a in agents if a.agent_type != "thief"]
    if rescue_agents:
        best = max(rescue_agents, key=lambda x: x.score)
        print(f"Winner: {best.name} ({best.agent_type}) with score {best.score:.2f}")
    print("="*60)

if __name__ == "__main__":
    main()