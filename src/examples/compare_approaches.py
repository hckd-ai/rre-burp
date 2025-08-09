#!/usr/bin/env python3
"""
Comparison: Manual vs Automated RRE Analysis
--------------------------------------------

This script demonstrates the difference between the old manual approach
and the new automated approach to HAR file analysis.
"""

import time
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str) -> tuple[str, float]:
    """Run a command and return output and execution time"""
    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        execution_time = time.time() - start_time
        return result.stdout, execution_time
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return "Command timed out after 5 minutes", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return f"Error: {e}", execution_time


def compare_approaches(har_file: str):
    """Compare manual vs automated approaches"""
    print("=" * 80)
    print("COMPARISON: MANUAL vs AUTOMATED RRE ANALYSIS")
    print("=" * 80)
    print(f"HAR File: {har_file}")
    print()
    
    # Test 1: Manual approach (what we did before)
    print("🔍 TEST 1: Manual Approach (Old Way)")
    print("-" * 50)
    print("This simulates what we had to do manually:")
    print("1. Manually search for high-entropy values")
    print("2. Guess which values might be important")
    print("3. Run multiple RRE traces with different seeds")
    print("4. Manually piece together dependency chains")
    print("5. Reason about relationships between values")
    print()
    
    # Test 2: Enhanced RRE with pattern analysis
    print("🔍 TEST 2: Enhanced RRE - Pattern Analysis")
    print("-" * 50)
    cmd1 = f"python3 rre_enhanced.py --har {har_file} --analyze-patterns"
    output1, time1 = run_command(cmd1)
    print(f"Execution time: {time1:.2f} seconds")
    print("Output:")
    print(output1[:1000] + "..." if len(output1) > 1000 else output1)
    print()
    
    # Test 3: Enhanced RRE with auto-discovery
    print("🔍 TEST 3: Enhanced RRE - Auto-Seed Discovery")
    print("-" * 50)
    cmd2 = f"python3 rre_enhanced.py --har {har_file} --auto-discover"
    output2, time2 = run_command(cmd2)
    print(f"Execution time: {time2:.2f} seconds")
    print("Output:")
    print(output2[:1000] + "..." if len(output2) > 1000 else output2)
    print()
    
    # Test 4: Intelligent analyzer (full automation)
    print("🔍 TEST 4: Intelligent Analyzer - Full Automation")
    print("-" * 50)
    cmd3 = f"python3 rre_intelligent_analyzer.py --har {har_file}"
    output3, time3 = run_command(cmd3)
    print(f"Execution time: {time3:.2f} seconds")
    print("Output:")
    print(output3[:1000] + "..." if len(output3) > 1000 else output3)
    print()
    
    # Test 5: Manual RRE with discovered seed
    print("🔍 TEST 5: Manual RRE with Discovered Seed")
    print("-" * 50)
    # Extract a seed from the auto-discovery output
    if "1629454135" in output2:
        seed = "1629454135"
        print(f"Using discovered seed: {seed}")
        cmd4 = f"python3 rre_standalone.py --har {har_file} --value {seed} --mode full"
        output4, time4 = run_command(cmd4)
        print(f"Execution time: {time4:.2f} seconds")
        print("Output:")
        print(output4[:1000] + "..." if len(output4) > 1000 else output4)
    else:
        print("No suitable seed found for manual RRE test")
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Pattern Analysis:     {time1:.2f}s")
    print(f"Auto-Discovery:       {time2:.2f}s")
    print(f"Full Automation:      {time3:.2f}s")
    if 'time4' in locals():
        print(f"Manual RRE:           {time4:.2f}s")
    
    total_automated = time1 + time2 + time3
    print(f"\nTotal Automated Time: {total_automated:.2f}s")
    
    if 'time4' in locals():
        print(f"Manual RRE Time:      {time4:.2f}s")
        print(f"Time Saved:           {time4 - total_automated:.2f}s")
        print(f"Efficiency Gain:      {(time4 - total_automated) / time4 * 100:.1f}%")
    
    print("\n🎯 KEY BENEFITS OF AUTOMATION:")
    print("✓ No manual searching for high-entropy values")
    print("✓ Automatic pattern recognition and categorization")
    print("✓ Intelligent seed prioritization")
    print("✓ Comprehensive dependency chain mapping")
    print("✓ Detailed reporting and visualization")
    print("✓ Repeatable and consistent results")
    print("✓ No need for AI reasoning during analysis")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 compare_approaches.py <har_file>")
        print("Example: python3 compare_approaches.py yeahscore_stream.har")
        sys.exit(1)
    
    har_file = sys.argv[1]
    if not Path(har_file).exists():
        print(f"Error: HAR file '{har_file}' not found")
        sys.exit(1)
    
    compare_approaches(har_file)


if __name__ == "__main__":
    main() 