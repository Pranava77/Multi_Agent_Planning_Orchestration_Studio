"""
Planning & Reasoning Engine
Implements:
1. TaskDecomposer: Generates Directed Acyclic Graph (DAG) of subtasks with dependency mapping.
2. DynamicReplanner: Evaluates intermediate results, catches unexpected conditions, and adapts subtasks.
3. Planning Strategies: Plan-and-Solve vs ReAct vs Plan-and-Execute with Dynamic Replanning.
"""

from typing import Dict, Any, List, Optional
import uuid

class TaskDecomposer:
    """
    Decomposes user queries into an actionable DAG of subtasks.
    Assigns each subtask to the most capable specialist agent.
    """
    
    @staticmethod
    def decompose_goal(user_query: str) -> List[Dict[str, Any]]:
        """Decomposes a query into structured subtasks with dependencies."""
        q_lower = user_query.lower()
        
        # Scenario 1: Financial Performance & Revenue Audit
        if "revenue" in q_lower or "ebitda" in q_lower or "400m" in q_lower or "financial" in q_lower:
            return [
                {
                    "id": "task_1_sql",
                    "title": "Extract FY2025 Quarterly Revenue Records",
                    "agent": "DataSQL-Specialist",
                    "goal": "Query quarterly_revenue table for FY2025 quarters, revenue, operating costs, and EBITDA.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"sql_query": "SELECT quarter, fiscal_year, revenue_millions, target_millions, operating_cost_millions, ebitda_millions FROM quarterly_revenue WHERE fiscal_year = 2025 ORDER BY quarter ASC;"}
                },
                {
                    "id": "task_2_kb",
                    "title": "Retrieve Strategic Financial Guidance",
                    "agent": "SupervisorAgent",
                    "goal": "Search knowledge documents for FY2025 targets, EBITDA thresholds, and investor representations.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"search_query": "FY2025 revenue target EBITDA margin"}
                },
                {
                    "id": "task_3_math",
                    "title": "Compute Total Revenue, EBITDA & QoQ Growth",
                    "agent": "Quant-Analyst",
                    "goal": "Run Python script to sum FY2025 quarterly revenue, aggregate EBITDA, and compute EBITDA margin %.",
                    "depends_on": ["task_1_sql"],
                    "status": "pending",
                    "params": {}
                },
                {
                    "id": "task_4_audit",
                    "title": "Adversarial Fact-Check & Discrepancy Audit",
                    "agent": "Critical-Reviewer",
                    "goal": "Audit claimed $400M revenue statement against verified $338.2M ledger and flag discrepancies.",
                    "depends_on": ["task_1_sql", "task_3_math"],
                    "status": "pending",
                    "params": {"claim": "Executive claimed FY2025 total revenue reached $400M with 60% growth."}
                },
                {
                    "id": "task_5_synthesis",
                    "title": "Synthesize Executive Multi-Agent Audit Report",
                    "agent": "Orchestrator-Prime",
                    "goal": "Collate findings into executive briefing with evidence tables and audit certification.",
                    "depends_on": ["task_1_sql", "task_2_kb", "task_3_math", "task_4_audit"],
                    "status": "pending",
                    "params": {}
                }
            ]

        # Scenario 2: Churn Risk Assessment & SLA Escalation
        elif "churn" in q_lower or "risk" in q_lower or "retention" in q_lower:
            return [
                {
                    "id": "task_1_sql",
                    "title": "Extract High-Risk Churn Accounts",
                    "agent": "DataSQL-Specialist",
                    "goal": "Query customer_churn for accounts with churn_risk_score >= 0.70.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"sql_query": "SELECT company_name, tier, annual_contract_value, churn_risk_score, primary_risk_factor, status FROM customer_churn WHERE churn_risk_score >= 0.70 ORDER BY churn_risk_score DESC;"}
                },
                {
                    "id": "task_2_kb",
                    "title": "Retrieve Churn Remediation SLA Policies",
                    "agent": "SupervisorAgent",
                    "goal": "Search knowledge docs for Tier-1 churn remediation playbooks and SLA timelines.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"search_query": "churn mitigation protocol SLA threshold"}
                },
                {
                    "id": "task_3_math",
                    "title": "Quantify Total Revenue at Risk (ACV Exposure)",
                    "agent": "Quant-Analyst",
                    "goal": "Calculate aggregate ACV at risk and average risk profile across flagged clients.",
                    "depends_on": ["task_1_sql"],
                    "status": "pending",
                    "params": {}
                },
                {
                    "id": "task_4_audit",
                    "title": "Verify Churn Risk Severity & Root Causes",
                    "agent": "Critical-Reviewer",
                    "goal": "Verify whether Alpha Robotics status matches SLA escalation threshold.",
                    "depends_on": ["task_1_sql", "task_3_math"],
                    "status": "pending",
                    "params": {"claim": "Alpha Robotics has healthy contract stability with low churn likelihood."}
                },
                {
                    "id": "task_5_synthesis",
                    "title": "Deliver Churn War-Room Action Plan",
                    "agent": "Orchestrator-Prime",
                    "goal": "Assemble strategic retention roadmap with account-by-account assignments.",
                    "depends_on": ["task_1_sql", "task_2_kb", "task_3_math", "task_4_audit"],
                    "status": "pending",
                    "params": {}
                }
            ]

        # Scenario 3: Sales Rep Performance & Commission Audit
        elif "sales" in q_lower or "rep" in q_lower or "deal" in q_lower or "marcus" in q_lower:
            return [
                {
                    "id": "task_1_sql",
                    "title": "Extract FY2025 Closed-Won Deals by Rep",
                    "agent": "DataSQL-Specialist",
                    "goal": "Fetch sales deals for Marcus Vance and other top account executives.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"sql_query": "SELECT client_name, industry, region, deal_size_usd, stage, close_quarter, account_executive FROM sales_deals WHERE account_executive = 'Marcus Vance' AND stage = 'Closed-Won';"}
                },
                {
                    "id": "task_2_kb",
                    "title": "Retrieve Sales Incentive Policies",
                    "agent": "SupervisorAgent",
                    "goal": "Search knowledge documents for Tier-1 closed-won commission benchmarks.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"search_query": "sales incentive deal qualification matrix"}
                },
                {
                    "id": "task_3_math",
                    "title": "Calculate Total Closed Revenue & Deal Averages",
                    "agent": "Quant-Analyst",
                    "goal": "Compute exact total closed-won contract value and mean deal size.",
                    "depends_on": ["task_1_sql"],
                    "status": "pending",
                    "params": {}
                },
                {
                    "id": "task_4_audit",
                    "title": "Audit $10M+ Performance Representation",
                    "agent": "Critical-Reviewer",
                    "goal": "Verify claim that Marcus Vance surpassed $10M in FY2025 closed revenue.",
                    "depends_on": ["task_1_sql", "task_3_math"],
                    "status": "pending",
                    "params": {"claim": "Marcus Vance closed over 10M in contracts during FY2025."}
                },
                {
                    "id": "task_5_synthesis",
                    "title": "Deliver Verified Sales Performance Review",
                    "agent": "Orchestrator-Prime",
                    "goal": "Deliver executive assessment with reconciled numbers and audit certification.",
                    "depends_on": ["task_1_sql", "task_2_kb", "task_3_math", "task_4_audit"],
                    "status": "pending",
                    "params": {}
                }
            ]

        # Default Generic Multi-Agent Workflow
        else:
            return [
                {
                    "id": "task_1_sql",
                    "title": "Inspect Enterprise Data Assets",
                    "agent": "DataSQL-Specialist",
                    "goal": "Query enterprise database metadata and schema tables.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"sql_query": "SELECT * FROM departments ORDER BY annual_budget_usd DESC;"}
                },
                {
                    "id": "task_2_kb",
                    "title": "Retrieve Relevant Organizational Policies",
                    "agent": "SupervisorAgent",
                    "goal": "Fetch relevant enterprise guidelines for query grounding.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"search_query": user_query}
                },
                {
                    "id": "task_3_math",
                    "title": "Quantitative Modeling & Metrics",
                    "agent": "Quant-Analyst",
                    "goal": "Compute summary statistics and allocation proportions.",
                    "depends_on": ["task_1_sql"],
                    "status": "pending",
                    "params": {}
                },
                {
                    "id": "task_4_audit",
                    "title": "Consistency & Compliance Verification",
                    "agent": "Critical-Reviewer",
                    "goal": "Verify claims against organizational evidence.",
                    "depends_on": ["task_1_sql", "task_3_math"],
                    "status": "pending",
                    "params": {"claim": "AI Platforms department has 42 members led by Dr. Clara Zhao."}
                },
                {
                    "id": "task_5_synthesis",
                    "title": "Deliver Strategic Intelligence Synthesis",
                    "agent": "Orchestrator-Prime",
                    "goal": "Deliver structured briefing with verifiable citations.",
                    "depends_on": ["task_1_sql", "task_2_kb", "task_3_math", "task_4_audit"],
                    "status": "pending",
                    "params": {}
                }
            ]


class DynamicReplanner:
    """
    Evaluates intermediate outputs in real time.
    If an unexpected condition occurs (e.g. SQL error, 0 rows, high discrepancy),
    it dynamically modifies the DAG, injecting corrective or fallback tasks.
    """
    
    @staticmethod
    def evaluate_and_replan(
        completed_task: Dict[str, Any],
        task_output: Dict[str, Any],
        remaining_tasks: List[Dict[str, Any]],
        blackboard: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inspects completed task results.
        Returns:
            {
                "replanning_triggered": bool,
                "reason": str,
                "action_taken": str,
                "updated_remaining_tasks": List[Dict[str, Any]]
            }
        """
        task_id = completed_task.get("id", "")
        
        # Guard against recursive replanning loops
        if task_id in ["task_sql_fallback", "task_audit_deepdive"]:
            return {
                "replanning_triggered": False,
                "reason": f"Corrective task '{task_id}' completed successfully.",
                "action_taken": "Proceeding to next planned step.",
                "updated_remaining_tasks": remaining_tasks
            }
        
        # 1. SQL Query Failure or Zero Results
        if "sql" in task_id and not any(t.get("id") == "task_sql_fallback" for t in remaining_tasks):
            sql_res = task_output.get("result") or task_output.get("observation", {})
            if not isinstance(sql_res, dict) or not sql_res.get("success", False) or sql_res.get("row_count", 0) == 0:
                # Dynamic replanning: inject fallback schema inquiry task
                fallback_task = {
                    "id": "task_sql_fallback",
                    "title": "Dynamic Schema Fallback & Wildcard Search",
                    "agent": "DataSQL-Specialist",
                    "goal": "Inspect sqlite_master schema and perform broader table query.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"sql_query": "SELECT * FROM departments;"}
                }
                new_remaining = [fallback_task] + remaining_tasks
                return {
                    "replanning_triggered": True,
                    "reason": f"SQL execution returned empty results or error: {sql_res.get('error', '0 rows') if isinstance(sql_res, dict) else 'Execution failure'}.",
                    "action_taken": "Injected 'task_sql_fallback' to re-query with broader schema inspection before proceeding to computational analysis.",
                    "updated_remaining_tasks": new_remaining
                }

        # 2. Critical Discrepancy Found in Audit
        if "audit" in task_id and not any(t.get("id") == "task_audit_deepdive" for t in remaining_tasks):
            audit_res = task_output.get("result") or task_output.get("observation", {})
            discrepancies = audit_res.get("discrepancies_found", []) if isinstance(audit_res, dict) else []
            if len(discrepancies) > 0:
                # Dynamic replanning: inject Root-Cause Discrepancy Decomposition subtask
                investigation_task = {
                    "id": "task_audit_deepdive",
                    "title": "Adversarial Root-Cause Discrepancy Deep-Dive",
                    "agent": "Critical-Reviewer",
                    "goal": "Isolate exact ledger lines responsible for the numerical discrepancy.",
                    "depends_on": [],
                    "status": "pending",
                    "params": {"claim": f"Investigate variance: {discrepancies[0]}"}
                }
                new_remaining = [investigation_task] + remaining_tasks
                return {
                    "replanning_triggered": True,
                    "reason": f"Critical Discrepancy detected during audit ({len(discrepancies)} mismatch(es)).",
                    "action_taken": "Dynamically added adversarial deep-dive audit task before final synthesis.",
                    "updated_remaining_tasks": new_remaining
                }

        return {
            "replanning_triggered": False,
            "reason": "Step completed within expected operational tolerances.",
            "action_taken": "Proceeding with current DAG sequence.",
            "updated_remaining_tasks": remaining_tasks
        }
