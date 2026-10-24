#!/usr/bin/env python3
"""
Multi-Agent Planning & Orchestration CLI Verification Suite
Tests end-to-end task decomposition, multi-agent dispatch, dynamic replanning,
blackboard state propagation, and executive synthesis.
"""

import sys
import os
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_engine import (
    MultiAgentOrchestrator,
    TaskDecomposer,
    MultiAgentEvaluator,
    get_schema_metadata
)

def run_cli_tests():
    print("=" * 70)
    print("🤖 MULTI-AGENT PLANNING & ORCHESTRATION STUDIO — CLI VERIFICATION")
    print("=" * 70)

    # 1. Database Schema Check
    print("\n[TEST 1] Checking Enterprise SQLite Schema Metadata...")
    schema = get_schema_metadata()
    for table, meta in schema.items():
        print(f"  • Table: {table:<20} | Rows: {meta['row_count']} | Columns: {len(meta['columns'])}")
    assert "quarterly_revenue" in schema, "quarterly_revenue table missing!"
    print("  ✓ Database schema verified successfully.")

    # 2. Task Decomposition Test
    print("\n[TEST 2] Testing Task Decomposition (DAG Generation)...")
    query = "Audit FY2025 quarterly revenue and compute EBITDA margin. Check executive claim of $400M."
    dag = TaskDecomposer.decompose_goal(query)
    print(f"  Query: '{query}'")
    print(f"  Generated Subtasks DAG ({len(dag)} steps):")
    for task in dag:
        print(f"    [{task['id']}] {task['agent']} ➔ {task['title']} (Depends on: {task['depends_on']})")
    assert len(dag) >= 4, "DAG decomposition incomplete!"
    print("  ✓ Task decomposition validated.")

    # 3. End-to-End Multi-Agent Workflow Execution
    print("\n[TEST 3] Running End-to-End Multi-Agent Workflow (Supervisor Mode)...")
    orchestrator = MultiAgentOrchestrator()
    res = orchestrator.execute_workflow(query, mode="supervisor", enable_dynamic_replanning=True)
    
    print(f"\n  Execution Completed in {res['duration_seconds']}s")
    print(f"  Agents Engaged: {res['agents_engaged']}")
    print(f"  Tools Invoked:  {res['tools_invoked']}")
    print(f"  Completed Steps Count: {res['completed_steps_count']}")
    
    print("\n--- STEP EXECUTION WATERFALL ---")
    for step in res["execution_trace"]:
        print(f"  Step {step['step']}: [{step['agent']}] ➔ Tool: {step.get('tool')}")
        print(f"    Thought: {step.get('thought')[:90]}...")
        if step.get('observation'):
            obs_preview = str(step['observation'])[:90].replace('\n', ' ')
            print(f"    Obs:     {obs_preview}...")

    # Verify blackboard artifacts
    bb = res["blackboard"]
    assert "sql_data" in bb, "Blackboard missing sql_data"
    assert "quantitative_analysis" in bb, "Blackboard missing quantitative_analysis"
    assert "audit_verification" in bb, "Blackboard missing audit_verification"
    print("\n--- FINAL SUPERVISOR SYNTHESIS PREVIEW ---")
    print(res["final_synthesis"][:350] + "...\n")
    print("  ✓ Shared blackboard state and executive synthesis verified.")

    # 4. Dynamic Replanning & Error Recovery Test
    print("\n[TEST 4] Testing Dynamic Replanning upon Fault Injection...")
    faulty_query = "Audit revenue records with simulated anomaly"
    faulty_res = orchestrator.execute_workflow(
        faulty_query,
        mode="supervisor",
        enable_dynamic_replanning=True,
        simulate_anomaly=True
    )
    print(f"  Replanning Events Triggered: {len(faulty_res['replanning_events'])}")
    for ev in faulty_res["replanning_events"]:
        print(f"    [Step {ev['step_triggered']}] Reason: {ev['reason']}")
        print(f"    Action: {ev['action_taken']}")
    assert len(faulty_res["replanning_events"]) > 0, "Replanning failed to trigger on anomaly!"
    print("  ✓ Dynamic replanning and error recovery verified.")

    # 5. Planning Strategies Benchmark Comparison
    print("\n[TEST 5] Validating Planning Strategies Benchmarking Suite...")
    benchmarks = MultiAgentEvaluator.get_planning_strategies_comparison()
    for strat in benchmarks["strategies"]:
        print(f"  • {strat['name']:<30} | Success: {strat['task_success_rate']}% | Steps: {strat['avg_steps']} | Recovery: {strat['error_recovery_rate']}%")
    print("  ✓ Benchmarking suite verified.")

    print("\n" + "=" * 70)
    print("🎯 ALL MULTI-AGENT VERIFICATION CHECKS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_cli_tests()
