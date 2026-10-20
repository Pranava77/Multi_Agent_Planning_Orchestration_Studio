"""
Multi-Agent Orchestrator
Coordinates multi-agent collaboration across:
- Supervisor / Hierarchical Orchestration Pattern
- Sequential Assembly Line Pipeline Pattern
- Dynamic Replanning with shared Blackboard working memory
"""

import time
from typing import Dict, Any, List, Optional
from .roles import (
    SupervisorAgent,
    DataSQLSpecialistAgent,
    QuantitativeAnalystAgent,
    CriticalReviewerAgent
)
from .planner import TaskDecomposer, DynamicReplanner
from .tools import search_enterprise_knowledge


class MultiAgentOrchestrator:
    """
    Coordinates multi-agent workflows, dispatches subtasks to specialist agents,
    maintains shared blackboard memory, and supports dynamic DAG replanning.
    """
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.sql_specialist = DataSQLSpecialistAgent()
        self.analyst = QuantitativeAnalystAgent()
        self.reviewer = CriticalReviewerAgent()
        
        self.agent_map = {
            "Orchestrator-Prime": self.supervisor,
            "SupervisorAgent": self.supervisor,
            "DataSQL-Specialist": self.sql_specialist,
            "Quant-Analyst": self.analyst,
            "Critical-Reviewer": self.reviewer
        }

    def get_agent_metadata(self) -> List[Dict[str, Any]]:
        """Returns metadata for all available agents."""
        return [
            self.supervisor.to_dict(),
            self.sql_specialist.to_dict(),
            self.analyst.to_dict(),
            self.reviewer.to_dict()
        ]

    def execute_workflow(
        self,
        user_query: str,
        mode: str = "supervisor",
        enable_dynamic_replanning: bool = True,
        simulate_anomaly: bool = False
    ) -> Dict[str, Any]:
        """
        Executes multi-agent workflow.
        Modes: 'supervisor', 'pipeline'
        """
        start_time = time.time()
        blackboard: Dict[str, Any] = {
            "user_query": user_query,
            "workflow_mode": mode,
            "dynamic_replanning_enabled": enable_dynamic_replanning
        }
        
        execution_trace: List[Dict[str, Any]] = []
        replanning_events: List[Dict[str, Any]] = []
        
        # Step 0: Task Decomposition
        initial_dag = TaskDecomposer.decompose_goal(user_query)
        
        # If simulating an anomaly, deliberately inject a faulty query or assertion
        if simulate_anomaly:
            if initial_dag:
                initial_dag[0]["params"]["sql_query"] = "SELECT * FROM non_existent_anomaly_table;"
        
        remaining_dag = list(initial_dag)
        completed_tasks = []
        step_number = 1
        max_steps = 15
        
        while remaining_dag and step_number <= max_steps:
            current_task = remaining_dag.pop(0)
            task_id = current_task["id"]
            agent_name = current_task["agent"]
            task_title = current_task["title"]
            params = current_task.get("params", {})
            
            # Execute step based on agent assignment
            step_record = {
                "step": step_number,
                "task_id": task_id,
                "title": task_title,
                "agent": agent_name,
                "status": "in_progress"
            }
            
            if agent_name == "DataSQL-Specialist":
                result = self.sql_specialist.execute_subtask(current_task["goal"], params)
                blackboard["sql_data"] = result["result"]
                step_record.update({
                    "thought": result["trace_step"]["thought"],
                    "action": result["trace_step"]["action"],
                    "tool": result["trace_step"]["tool"],
                    "observation": result["trace_step"]["observation"],
                    "result": result["result"],
                    "status": "success" if result["result"].get("success") else "warning"
                })
                
            elif agent_name == "SupervisorAgent" or (agent_name == "Orchestrator-Prime" and "kb" in task_id):
                search_q = params.get("search_query", user_query)
                kb_res = search_enterprise_knowledge(search_q)
                blackboard["knowledge_context"] = kb_res
                thought = f"Supervisor retrieving enterprise knowledge documents for query '{search_q}'."
                action_log = self.supervisor.log_action(
                    thought=thought,
                    action=f"Searching knowledge repository: {search_q}",
                    tool_name="search_enterprise_knowledge",
                    observation=kb_res
                )
                step_record.update({
                    "thought": thought,
                    "action": action_log["action"],
                    "tool": action_log["tool"],
                    "observation": kb_res,
                    "result": kb_res,
                    "status": "success"
                })
                
            elif agent_name == "Quant-Analyst":
                result = self.analyst.execute_subtask(current_task["goal"], blackboard.get("sql_data"), params)
                blackboard["quantitative_analysis"] = result["result"]
                step_record.update({
                    "thought": result["trace_step"]["thought"],
                    "action": result["trace_step"]["action"],
                    "tool": result["trace_step"]["tool"],
                    "observation": result["trace_step"]["observation"],
                    "result": result["result"],
                    "status": "success" if result["result"].get("success") else "warning"
                })
                
            elif agent_name == "Critical-Reviewer":
                claim = params.get("claim", user_query)
                result = self.reviewer.execute_subtask(current_task["goal"], claim, blackboard)
                blackboard["audit_verification"] = result["result"]
                step_record.update({
                    "thought": result["trace_step"]["thought"],
                    "action": result["trace_step"]["action"],
                    "tool": result["trace_step"]["tool"],
                    "observation": result["trace_step"]["observation"],
                    "result": result["result"],
                    "status": "warning" if result["result"].get("discrepancies_found") else "success"
                })
                
            elif agent_name == "Orchestrator-Prime" and "synthesis" in task_id:
                syn_result = self.supervisor.synthesize(user_query, blackboard)
                blackboard["final_synthesis"] = syn_result["final_synthesis"]
                step_record.update({
                    "thought": syn_result["trace_step"]["thought"],
                    "action": syn_result["trace_step"]["action"],
                    "tool": syn_result["trace_step"]["tool"],
                    "observation": syn_result["trace_step"]["observation"],
                    "status": "success"
                })
            else:
                # Fallback task execution
                step_record.update({
                    "thought": f"Executing fallback subtask {task_title}",
                    "action": f"Task goal: {current_task['goal']}",
                    "tool": "general_processor",
                    "observation": {"status": "Task executed"},
                    "status": "success"
                })

            execution_trace.append(step_record)
            completed_tasks.append(current_task)
            step_number += 1
            
            # Dynamic Replanning Check
            if enable_dynamic_replanning and remaining_dag:
                replan_eval = DynamicReplanner.evaluate_and_replan(
                    completed_task=current_task,
                    task_output=step_record,
                    remaining_tasks=remaining_dag,
                    blackboard=blackboard
                )
                if replan_eval["replanning_triggered"]:
                    replanning_events.append({
                        "step_triggered": step_record["step"],
                        "task_id": task_id,
                        "reason": replan_eval["reason"],
                        "action_taken": replan_eval["action_taken"]
                    })
                    remaining_dag = replan_eval["updated_remaining_tasks"]

        # Ensure final synthesis is populated
        if "final_synthesis" not in blackboard:
            syn_result = self.supervisor.synthesize(user_query, blackboard)
            blackboard["final_synthesis"] = syn_result["final_synthesis"]
            
        elapsed_sec = round(time.time() - start_time, 3)
        
        # Tally metrics
        agents_engaged = list(set([step["agent"] for step in execution_trace]))
        tools_invoked = [step["tool"] for step in execution_trace if step.get("tool")]
        
        return {
            "user_query": user_query,
            "mode": mode,
            "initial_dag": initial_dag,
            "completed_steps_count": len(execution_trace),
            "execution_trace": execution_trace,
            "replanning_events": replanning_events,
            "agents_engaged": agents_engaged,
            "tools_invoked": tools_invoked,
            "blackboard": blackboard,
            "final_synthesis": blackboard.get("final_synthesis", ""),
            "duration_seconds": elapsed_sec
        }
