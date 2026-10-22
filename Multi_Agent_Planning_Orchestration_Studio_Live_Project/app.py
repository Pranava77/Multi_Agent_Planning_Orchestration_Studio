"""
Multi-Agent Planning & Orchestration Studio — FastAPI Server
Port: 8210
Serves the 5-Tab interactive dashboard and REST endpoints for multi-agent workflows,
planning decomposition, dynamic replanning simulation, and LLMOps benchmarks.
"""

import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from multi_agent_engine import (
    MultiAgentOrchestrator,
    TaskDecomposer,
    MultiAgentEvaluator,
    get_schema_metadata,
    execute_sql_query,
    execute_python_calc,
    search_enterprise_knowledge,
    verify_audit_claims
)

app = FastAPI(
    title="Multi-Agent Planning & Orchestration Studio",
    description="Enterprise Multi-Agent Workflow, Task Decomposition, Dynamic Replanning & Fact-Checking Studio",
    version="1.0.0"
)

# Static & Template directories
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Shared Orchestrator instance
orchestrator = MultiAgentOrchestrator()


class OrchestrationRequest(BaseModel):
    query: str
    mode: Optional[str] = "supervisor"
    enable_dynamic_replanning: Optional[bool] = True
    simulate_anomaly: Optional[bool] = False


class DecomposeRequest(BaseModel):
    query: str


class ToolTestRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
async def index():
    """Renders the main 5-tab dashboard."""
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Multi-Agent Planning Studio</h1><p>index.html not found</p>"


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Multi-Agent Planning & Orchestration Studio",
        "port": 8210,
        "agents_available": 4,
        "database_connected": True
    }


@app.get("/api/roles")
async def get_roles():
    """Returns metadata for the 4 specialist agent roles."""
    return {
        "agents": orchestrator.get_agent_metadata()
    }


@app.get("/api/schema")
async def get_db_schema():
    """Returns enterprise database schema metadata."""
    return get_schema_metadata()


@app.post("/api/decompose")
async def decompose_task(req: DecomposeRequest):
    """Decomposes a user goal into an ordered DAG of subtasks."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    dag = TaskDecomposer.decompose_goal(req.query)
    return {
        "query": req.query,
        "subtasks_count": len(dag),
        "dag": dag
    }


@app.post("/api/orchestrate")
async def run_orchestration(req: OrchestrationRequest):
    """Executes full multi-agent collaborative workflow."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    result = orchestrator.execute_workflow(
        user_query=req.query,
        mode=req.mode or "supervisor",
        enable_dynamic_replanning=req.enable_dynamic_replanning if req.enable_dynamic_replanning is not None else True,
        simulate_anomaly=req.simulate_anomaly or False
    )
    return result


@app.get("/api/benchmarks")
async def get_benchmarks():
    """Returns quantitative comparison data for planning strategies and scenario evaluations."""
    comparison = MultiAgentEvaluator.get_planning_strategies_comparison()
    scenarios = MultiAgentEvaluator.get_benchmark_scenarios()
    return {
        "strategies_comparison": comparison,
        "scenarios": scenarios
    }


@app.post("/api/test_tool")
async def direct_tool_test(req: ToolTestRequest):
    """Allows direct testing of individual agent tools in Tab 3."""
    tool = req.tool_name
    params = req.params
    
    if tool == "execute_sql_query":
        q = params.get("query", "SELECT * FROM departments;")
        return execute_sql_query(q)
    elif tool == "execute_python_calc":
        code = params.get("code", "result = sum([10, 20, 30])")
        return execute_python_calc(code)
    elif tool == "search_enterprise_knowledge":
        q = params.get("query", "revenue target")
        return search_enterprise_knowledge(q)
    elif tool == "verify_audit_claims":
        claim = params.get("claim", "FY2025 revenue was $400M")
        return verify_audit_claims(claim, {})
    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool '{tool}'")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8210, reload=False)
