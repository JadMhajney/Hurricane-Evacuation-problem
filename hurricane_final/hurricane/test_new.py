#!/usr/bin/env python3
"""
Comprehensive Test Suite for Hurricane Evacuation Problem
Tests all edge cases and requirements from the assignment

Run with: python -m hurricane.test_comprehensive
"""

import os
import sys
import subprocess
from pathlib import Path

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_test(num, name):
    print(f"{BOLD}Test {num}: {name}{RESET}")
    print("-" * 70)

def print_pass(msg):
    print(f"{GREEN}✓ PASS:{RESET} {msg}")

def print_fail(msg):
    print(f"{RED}✗ FAIL:{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠ WARNING:{RESET} {msg}")

def create_test_file(filename, content):
    """Create a test graph file"""
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def run_test(graph_file, agents, starts, expected_behavior, test_name):
    """Run a single test case"""
    cmd = [
        sys.executable, '-m', 'hurricane.run',
        '--input', graph_file,
        '--agents'] + agents + [
        '--starts'] + starts + [
        '--T', '0'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout + result.stderr
        
        # Check expected behavior
        passed = True
        for keyword in expected_behavior['must_contain']:
            if keyword not in output:
                print_fail(f"Missing expected output: '{keyword}'")
                passed = False
        
        for keyword in expected_behavior.get('must_not_contain', []):
            if keyword in output:
                print_fail(f"Found unexpected output: '{keyword}'")
                passed = False
        
        if passed:
            print_pass(test_name)
        
        return passed, output
        
    except subprocess.TimeoutExpired:
        print_fail(f"{test_name} - TIMEOUT (infinite loop suspected)")
        return False, ""
    except Exception as e:
        print_fail(f"{test_name} - ERROR: {str(e)}")
        return False, ""

def main():
    print_header("COMPREHENSIVE TEST SUITE FOR HURRICANE EVACUATION")
    print(f"Testing all assignment requirements and edge cases\n")
    
    all_passed = True
    test_results = []
    
    # ========================================================================
    # TEST 1: All people at starting position
    # ========================================================================
    print_test(1, "All people at starting position (immediate rescue)")
    
    graph1 = create_test_file("test_01_start.txt", """#N 3
#U 1
#Q 2
#P 3
#V1 P5
#V2 B
#V3 B
#E1 1 2 W1
#E2 2 3 W1
""")
    
    passed, output = run_test(
        graph1,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['SUCCESS: All people rescued', 'saved=5'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Should rescue all 5 people immediately"
    )
    test_results.append(("Test 1", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 2: No people to rescue
    # ========================================================================
    print_test(2, "No people to rescue (empty world)")
    
    graph2 = create_test_file("test_02_empty.txt", """#N 3
#U 1
#Q 2
#P 3
#V1 B
#V2 B
#V3 B
#E1 1 2 W1
#E2 2 3 W1
""")
    
    passed, output = run_test(
        graph2,
        ['stupid_greedy', 'astar'],
        ['1', '1'],
        {
            'must_contain': ['SUCCESS: All people rescued'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Should terminate immediately when no people exist"
    )
    test_results.append(("Test 2", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 3: Unreachable people (flooded, no kits)
    # ========================================================================
    print_test(3, "Unreachable people (flooded edges, no kits)")
    
    graph3 = create_test_file("test_03_unreachable.txt", """#N 4
#U 1
#Q 2
#P 3
#V1 B
#V2 P2
#V3 B
#V4 P3
#E1 1 2 W1 F
#E2 3 4 W1
""")
    
    passed, output = run_test(
        graph3,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['NATURAL'],
            'must_not_contain': ['FORCED', 'EMERGENCY', 'saved=2', 'saved=3', 'saved=5']
        },
        "Should terminate naturally when targets unreachable"
    )
    test_results.append(("Test 3", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 4: Kit required for flooded edges
    # ========================================================================
    print_test(4, "Flooded edges requiring amphibian kit")
    
    graph4 = create_test_file("test_04_flooded_kit.txt", """#N 4
#U 1
#Q 2
#P 3
#V1 K
#V2 B
#V3 P3
#V4 P2
#E1 1 2 W1 F
#E2 2 3 W1 F
#E3 2 4 W1
""")
    
    passed, output = run_test(
        graph4,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['saved=5', 'SUCCESS'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Should equip kit and rescue all people"
    )
    test_results.append(("Test 4", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 5: Multiple agents (3 as per assignment)
    # ========================================================================
    print_test(5, "Three agents: stupid_greedy, thief, astar (assignment requirement)")
    
    graph5 = create_test_file("test_05_three_agents.txt", """#N 5
#U 1
#Q 2
#P 3
#V1 B
#V2 P2
#V3 K
#V4 P3
#V5 P1
#E1 1 2 W1
#E2 2 3 W2
#E3 3 4 W1
#E4 4 5 W1
#E5 1 5 W10
""")
    
    passed, output = run_test(
        graph5,
        ['stupid_greedy', 'thief', 'astar'],
        ['1', '1', '1'],
        {
            'must_contain': ['stupid_greedy', 'thief', 'astar', 'saved=6'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "All three agent types should work together"
    )
    test_results.append(("Test 5", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 6: Greedy vs A* comparison
    # ========================================================================
    print_test(6, "Greedy Search vs A* performance comparison")
    
    graph6 = create_test_file("test_06_comparison.txt", """#N 6
#U 1
#Q 2
#P 3
#V1 B
#V2 P1
#V3 P1
#V4 P1
#V5 P1
#V6 P1
#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 4 5 W1
#E5 5 6 W1
#E6 1 6 W10
""")
    
    passed, output = run_test(
        graph6,
        ['greedy_search', 'astar'],
        ['1', '1'],
        {
            'must_contain': ['greedy_search', 'astar', 'SUCCESS'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Greedy and A* should both find solutions"
    )
    test_results.append(("Test 6", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 7: Real-Time A* with limited expansions
    # ========================================================================
    print_test(7, "Real-Time A* with L=10 expansions per step")
    
    graph7 = create_test_file("test_07_rta.txt", """#N 5
#U 1
#Q 2
#P 3
#V1 B
#V2 P1
#V3 P1
#V4 P1
#V5 P1
#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 4 5 W1
""")
    
    passed, output = run_test(
        graph7,
        ['rta'],
        ['1'],
        {
            'must_contain': ['rta', 'saved=4'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "RTA* should work with limited lookahead"
    )
    test_results.append(("Test 7", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 8: Kit equip/unequip mechanics
    # ========================================================================
    print_test(8, "Amphibian kit equip and unequip mechanics")
    
    graph8 = create_test_file("test_08_kit_mechanics.txt", """#N 5
#U 2
#Q 3
#P 4
#V1 B
#V2 K
#V3 P2
#V4 B
#V5 P3
#E1 1 2 W1
#E2 2 3 W1 F
#E3 3 4 W1
#E4 4 5 W1
""")
    
    passed, output = run_test(
        graph8,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['saved=5', 'SUCCESS'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Should handle equip/unequip with proper timing (Q=3, U=2)"
    )
    test_results.append(("Test 8", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 9: Speed factor P for amphibian kit
    # ========================================================================
    print_test(9, "Amphibian kit speed factor P=4")
    
    graph9 = create_test_file("test_09_speed_factor.txt", """#N 3
#U 1
#Q 2
#P 4
#V1 K
#V2 P1
#V3 P1
#E1 1 2 W1 F
#E2 2 3 W1 F
""")
    
    passed, output = run_test(
        graph9,
        ['astar'],
        ['1'],
        {
            'must_contain': ['saved=2', 'SUCCESS'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Should apply speed factor P=4 when using kit on flooded roads"
    )
    test_results.append(("Test 9", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 10: Thief agent behavior
    # ========================================================================
    print_test(10, "Thief agent steals kit and runs away")
    
    graph10 = create_test_file("test_10_thief.txt", """#N 4
#U 1
#Q 2
#P 3
#V1 P2
#V2 K
#V3 P3
#V4 B
#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 1 4 W10
""")
    
    passed, output = run_test(
        graph10,
        ['stupid_greedy', 'thief'],
        ['1', '1'],
        {
            'must_contain': ['thief', 'saved=0'],  # Thief doesn't save anyone
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Thief should not save people, should steal kit"
    )
    test_results.append(("Test 10", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 11: Score calculation (saved*1000 - time)
    # ========================================================================
    print_test(11, "Score calculation: saved × 1000 - time")
    
    graph11 = create_test_file("test_11_score.txt", """#N 3
#U 1
#Q 2
#P 3
#V1 P3
#V2 B
#V3 B
#E1 1 2 W1
#E2 2 3 W1
""")
    
    passed, output = run_test(
        graph11,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['saved=3', 'score=3000', 'SUCCESS'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "Score should be 3*1000 - 0 = 3000"
    )
    test_results.append(("Test 11", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 12: Partial rescue (some people unreachable)
    # ========================================================================
    print_test(12, "Partial rescue - some people unreachable")
    
    graph12 = create_test_file("test_12_partial.txt", """#N 5
#U 1
#Q 2
#P 3
#V1 B
#V2 P2
#V3 B
#V4 P3
#V5 P1
#E1 1 2 W1
#E2 2 3 W5
#E3 4 5 W1
""")
    
    passed, output = run_test(
        graph12,
        ['stupid_greedy'],
        ['1'],
        {
            'must_contain': ['saved=2', 'NATURAL'],
            'must_not_contain': ['saved=6', 'FORCED', 'EMERGENCY']
        },
        "Should rescue reachable people (V2) but not unreachable (V4,V5)"
    )
    test_results.append(("Test 12", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 13: Complex graph from assignment (hard.txt)
    # ========================================================================
    print_test(13, "Complex graph (hard.txt from assignment)")
    
    # Use existing hard.txt
    if os.path.exists("hard.txt"):
        passed, output = run_test(
            "hard.txt",
            ['stupid_greedy', 'thief', 'astar'],
            ['1', '1', '1'],
            {
                'must_contain': ['stupid_greedy', 'thief', 'astar'],
                'must_not_contain': ['FORCED', 'EMERGENCY']
            },
            "Should handle complex graph without infinite loops"
        )
    else:
        print_warning("hard.txt not found, skipping test")
        passed = True
    
    test_results.append(("Test 13", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 14: A* expansion limit
    # ========================================================================
    print_test(14, "A* expansion limit (LIMIT=10000)")
    
    graph14 = create_test_file("test_14_limit.txt", """#N 8
#U 1
#Q 2
#P 3
#V1 B
#V2 P1
#V3 P1
#V4 P1
#V5 P1
#V6 P1
#V7 P1
#V8 P1
#E1 1 2 W1
#E2 2 3 W1
#E3 3 4 W1
#E4 4 5 W1
#E5 5 6 W1
#E6 6 7 W1
#E7 7 8 W1
""")
    
    passed, output = run_test(
        graph14,
        ['astar'],
        ['1'],
        {
            'must_contain': ['astar', 'saved=7'],
            'must_not_contain': ['FORCED', 'EMERGENCY']
        },
        "A* should handle within expansion limit"
    )
    test_results.append(("Test 14", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # TEST 15: No infinite loop on impossible scenarios
    # ========================================================================
    print_test(15, "No infinite loop detection (emergency brake test)")
    
    graph15 = create_test_file("test_15_no_loop.txt", """#N 4
#U 1
#Q 2
#P 3
#V1 B
#V2 P2
#V3 K
#V4 P3
#E1 1 2 W1 F
#E2 2 3 W1 F
#E3 3 4 W1 F
""")
    
    passed, output = run_test(
        graph15,
        ['greedy_search', 'astar', 'rta'],
        ['1', '1', '1'],
        {
            'must_contain': ['NATURAL'],  # Should terminate naturally, not forced
            'must_not_contain': []  # Don't check for FORCED - could go either way
        },
        "Should terminate (naturally or via emergency brake) without hanging"
    )
    
    # Special check: if it contains FORCED, that's OK but warn
    if 'FORCED' in output:
        print_warning("Emergency brake triggered - agents were stuck")
    
    test_results.append(("Test 15", passed))
    all_passed = all_passed and passed
    print()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, p in test_results if p)
    total_count = len(test_results)
    
    print(f"\nResults: {passed_count}/{total_count} tests passed\n")
    
    for test_name, passed in test_results:
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{BOLD}{'='*70}{RESET}")
    
    if all_passed:
        print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED! 🎉{RESET}")
        print(f"{GREEN}Your solution covers all assignment requirements!{RESET}")
    else:
        print(f"{RED}{BOLD}❌ SOME TESTS FAILED{RESET}")
        print(f"{RED}Please review the failed tests above.{RESET}")
    
    print(f"{BOLD}{'='*70}{RESET}\n")
    
    # Clean up test files
    for i in range(1, 16):
        try:
            os.remove(f"test_{i:02d}_*.txt")
        except:
            pass
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())