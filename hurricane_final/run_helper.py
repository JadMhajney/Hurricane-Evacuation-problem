#!/usr/bin/env python3
import sys
import subprocess

# ==========================================
# CONFIGURATION
# ==========================================
# List of agents to run. 
# Options: "human", "stupid_greedy", "thief", "greedy_search", "astar", "rta"
AGENTS = ["astar"] 
# AGENTS = ["astar", "greedy_search"] 

# ==========================================

def run_simulation(start_pos, test_file):
    """
    Run the simulation with the configured agents.
    
    Args:
        start_pos (int or list): Starting vertex number(s). 
                                 If single int, applies to first agent (or all if broadcast).
                                 If list, must match length of AGENTS.
        test_file (str): Name of the input graph file.
    """
    
    # Handle start_pos being a single int or a list
    if isinstance(start_pos, int):
        starts = [str(start_pos)] * len(AGENTS)
    else:
        starts = [str(s) for s in start_pos]

    cmd = [
        sys.executable, "-m", "hurricane.run",
        "--input", test_file,
        "--agents"
    ] + AGENTS + [
        "--starts"
    ] + starts
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # CHANGE THESE VALUES TO RUN DIFFERENT TESTS
    # ------------------------------------------
    run_simulation(start_pos=[1], test_file="test_14_limit.txt")


    # # If start_pos is a single number (e.g. 1), it applies to ALL agents.
    # # If start_pos is a list (e.g. [1, 2]), it assigns starts to agents in order.
    # run_simulation(start_pos=[1, 1], test_file="testAhmad.txt")
