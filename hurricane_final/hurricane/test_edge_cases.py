#!/usr/bin/env python3
"""
Edge case tests for Hurricane Evacuation Problem.
Run with: python -m hurricane.test_edge_cases
"""

def test_all_people_at_start():
    """Test: All people are at the starting vertex."""
    print("Test 1: All people at starting position")
    # Create test file
    content = """#N 3
#U 1
#Q 2
#P 3
#V1 P5
#V2 B
#V3 B
#E1 1 2 W1
#E2 2 3 W1
"""
    with open("test_start.txt", "w") as f:
        f.write(content)
    
    from .world import parse_world_from_file
    from .agents import StupidGreedyAgent, AgentState
    
    world, _ = parse_world_from_file("test_start.txt")
    agent = AgentState("A1", "stupid_greedy", pos=1)
    policy = StupidGreedyAgent()
    
    # Should pick up immediately
    world.pick_up_people(agent)
    assert agent.saved == 5, f"Expected 5 saved, got {agent.saved}"
    assert world.total_people() == 0, "All people should be rescued"
    print("✓ Test 1 passed\n")

def test_unreachable_people():
    """Test: People are on unreachable island."""
    print("Test 2: Unreachable people (no path)")
    content = """#N 4
#U 1
#Q 2
#P 3
#V1 B
#V2 P2
#V3 B
#V4 P3
#E1 1 2 W1 F
#E2 3 4 W1
"""
    with open("test_unreachable.txt", "w") as f:
        f.write(content)
    
    from .world import parse_world_from_file
    from .agents import StupidGreedyAgent, AgentState
    
    world, _ = parse_world_from_file("test_unreachable.txt")
    agent = AgentState("A1", "stupid_greedy", pos=1)
    policy = StupidGreedyAgent()
    
    action = policy(world, agent)
    # Should terminate (no kit available, can't cross flooded edge)
    assert action[0] == "terminate", f"Expected terminate, got {action[0]}"
    print("✓ Test 2 passed\n")

def test_no_people():
    """Test: No people to rescue."""
    print("Test 3: No people to rescue")
    content = """#N 3
#U 1
#Q 2
#P 3
#V1 B
#V2 B
#V3 B
#E1 1 2 W1
#E2 2 3 W1
"""
    with open("test_empty.txt", "w") as f:
        f.write(content)
    
    from .world import parse_world_from_file
    from .agents import StupidGreedyAgent, AgentState
    
    world, _ = parse_world_from_file("test_empty.txt")
    agent = AgentState("A1", "stupid_greedy", pos=1)
    policy = StupidGreedyAgent()
    
    action = policy(world, agent)
    assert action[0] == "terminate", "Should terminate when no people exist"
    print("✓ Test 3 passed\n")

def test_flooded_with_kit():
    """Test: Flooded edges with kit handling."""
    print("Test 4: Flooded edges requiring kit")
    content = """#N 3
#U 1
#Q 2
#P 3
#V1 K
#V2 B
#V3 P5
#E1 1 2 W1 F
#E2 2 3 W1 F
"""
    with open("test_flooded.txt", "w") as f:
        f.write(content)
    
    from .world import parse_world_from_file
    from .agents import StupidGreedyAgent, AgentState
    
    world, _ = parse_world_from_file("test_flooded.txt")
    agent = AgentState("A1", "stupid_greedy", pos=1)
    policy = StupidGreedyAgent()
    
    # First action should be EQUIP (kit at V1, targets exist, all paths flooded)
    action = policy(world, agent)
    assert action[0] == "equip", f"Should equip kit first, got {action[0]}"
    
    # Actually equip it
    world.do_action(agent, action)
    
    # Now should traverse
    action = policy(world, agent)
    assert action[0] == "traverse", f"After equipping, should traverse, got {action[0]}"
    
    print("✓ Test 4 passed\n")

if __name__ == "__main__":
    print("="*60)
    print("RUNNING EDGE CASE TESTS")
    print("="*60 + "\n")
    
    test_all_people_at_start()
    test_unreachable_people()
    test_no_people()
    test_flooded_with_kit()
    
    print("="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)