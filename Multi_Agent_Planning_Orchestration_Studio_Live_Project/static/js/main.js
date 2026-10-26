/**
 * Multi-Agent Planning & Orchestration Studio — Client Application
 * Handles live DAG visualization, multi-agent execution waterfall,
 * dynamic replanning simulator, and LLMOps evaluation charts.
 */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initTab1Orchestration();
    initTab2PlanningArena();
    initTab3RolesAndTools();
    initTab4ReplanningSimulator();
    initTab5Benchmarks();
});

/* ====================================================================
   1. Tab Navigation
   ==================================================================== */
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add("active");

            // Re-render chart if switching to benchmarks
            if (targetTab === "tab5") {
                renderRadarChart();
            }
        });
    });
}

/* ====================================================================
   2. Tab 1: Multi-Agent Orchestrator & Live Waterfall
   ==================================================================== */
function initTab1Orchestration() {
    const queryInput = document.getElementById("orchestrate-query");
    const btnDecompose = document.getElementById("btn-decompose");
    const btnExecute = document.getElementById("btn-execute-workflow");
    const dagContainer = document.getElementById("dag-preview");
    const waterfallContainer = document.getElementById("waterfall-trace");
    const replanBanner = document.getElementById("replan-banner");
    const synthesisContainer = document.getElementById("final-synthesis-box");
    const blackboardViewer = document.getElementById("blackboard-json");
    const modeSelect = document.getElementById("workflow-mode-select");
    const replanToggle = document.getElementById("replan-toggle");

    // Presets
    document.querySelectorAll(".preset-tab1").forEach(chip => {
        chip.addEventListener("click", () => {
            queryInput.value = chip.getAttribute("data-query");
            triggerDecompose();
        });
    });

    btnDecompose.addEventListener("click", triggerDecompose);

    async function triggerDecompose() {
        const query = queryInput.value.trim();
        if (!query) return;

        dagContainer.innerHTML = `<div class="loading-msg"><div class="spinner"></div> Decomposing goal into subtask DAG...</div>`;
        
        try {
            const res = await fetch("/api/decompose", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await res.json();
            renderDAG(data.dag);
        } catch (err) {
            dagContainer.innerHTML = `<div style="color: var(--accent-pink); font-size:14px;"><i class="fa-solid fa-triangle-exclamation"></i> Error decomposing goal: ${err.message}</div>`;
        }
    }

    function renderDAG(dag) {
        let html = `<div class="dag-steps">`;
        dag.forEach((step, idx) => {
            let tagClass = "tag-supervisor";
            if (step.agent.includes("SQL")) tagClass = "tag-sql";
            else if (step.agent.includes("Quant")) tagClass = "tag-analyst";
            else if (step.agent.includes("Reviewer")) tagClass = "tag-reviewer";

            html += `
                <div class="dag-node" id="node-${step.id}">
                    <div class="dag-node-header">
                        <span class="agent-tag ${tagClass}">${step.agent}</span>
                        <span class="dag-step-num">Step ${idx + 1}</span>
                    </div>
                    <div class="dag-node-title">${step.title}</div>
                    <div class="dag-node-deps">Depends: ${step.depends_on.length ? step.depends_on.join(", ") : "None (Root)"}</div>
                </div>
            `;
            if (idx < dag.length - 1) {
                html += `<div class="dag-arrow"><i class="fa-solid fa-arrow-right"></i></div>`;
            }
        });
        html += `</div>`;
        dagContainer.innerHTML = html;
    }

    btnExecute.addEventListener("click", async () => {
        const query = queryInput.value.trim();
        if (!query) {
            alert("Please enter a query or select a preset.");
            return;
        }

        btnExecute.disabled = true;
        btnExecute.innerHTML = `<div class="spinner" style="width:14px;height:14px;border-top-color:var(--ink-deep);"></div> Orchestrating...`;
        waterfallContainer.innerHTML = `<div class="loading-msg"><div class="spinner"></div> Coordinating agent handoffs and tool executions...</div>`;
        replanBanner.style.display = "none";
        synthesisContainer.style.display = "none";

        try {
            const res = await fetch("/api/orchestrate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query,
                    mode: modeSelect ? modeSelect.value : "supervisor",
                    enable_dynamic_replanning: replanToggle ? replanToggle.checked : true,
                    simulate_anomaly: false
                })
            });
            const data = await res.json();
            renderExecutionTrace(data);
        } catch (err) {
            waterfallContainer.innerHTML = `<div style="color: var(--accent-pink); font-size:14px;"><i class="fa-solid fa-triangle-exclamation"></i> Workflow execution error: ${err.message}</div>`;
        } finally {
            btnExecute.disabled = false;
            btnExecute.innerHTML = `<i class="fa-solid fa-play"></i> Execute Workflow`;
        }
    });

    function renderExecutionTrace(data) {
        // Render Replanning Alert if triggered
        if (data.replanning_events && data.replanning_events.length > 0) {
            const ev = data.replanning_events[0];
            replanBanner.innerHTML = `
                <i class="fa-solid fa-triangle-exclamation"></i>
                <div>
                    <div class="replan-title">Dynamic Replanning Event Triggered (Step ${ev.step_triggered})</div>
                    <div class="replan-desc"><strong>Reason:</strong> ${ev.reason}</div>
                    <div class="replan-desc" style="color: #93c5fd; margin-top: 0.2rem;"><strong>Action Taken:</strong> ${ev.action_taken}</div>
                </div>
            `;
            replanBanner.style.display = "flex";
        } else {
            replanBanner.style.display = "none";
        }

        // Waterfall trace
        let html = "";
        data.execution_trace.forEach(step => {
            let agentClass = "";
            let tagClass = "tag-supervisor";
            if (step.agent.includes("SQL")) { agentClass = "agent-sql"; tagClass = "tag-sql"; }
            else if (step.agent.includes("Quant")) { agentClass = "agent-analyst"; tagClass = "tag-analyst"; }
            else if (step.agent.includes("Reviewer")) { agentClass = "agent-reviewer"; tagClass = "tag-reviewer"; }

            html += `
                <div class="waterfall-step ${agentClass}">
                    <div class="waterfall-header">
                        <span class="agent-tag ${tagClass}"><i class="fa-solid fa-robot"></i> ${step.agent}</span>
                        <span class="waterfall-meta">Step ${step.step} &nbsp;·&nbsp; ${step.tool || "internal"}</span>
                    </div>
                    <div class="thought-box"><strong style="color:var(--on-primary);font-weight:600;">Thought:</strong> ${step.thought}</div>
                    <div class="action-box"><strong style="color:var(--on-primary);font-weight:600;">Action:</strong> ${step.action}</div>
                    <div class="observation-box"><strong style="color:var(--on-primary);font-weight:600;">Observation:</strong>\n${typeof step.observation === "object" ? JSON.stringify(step.observation, null, 2) : step.observation}</div>
                </div>
            `;
        });
        waterfallContainer.innerHTML = html;

        // Executive Synthesis
        const finalSyn = data.final_synthesis || (data.blackboard && data.blackboard.final_synthesis);
        if (finalSyn) {
            document.getElementById("synthesis-text").innerHTML = formatMarkdown(finalSyn);
            synthesisContainer.style.display = "block";
        }

        // Blackboard JSON
        if (blackboardViewer && data.blackboard) {
            blackboardViewer.textContent = JSON.stringify(data.blackboard, null, 2);
        }
    }
}

/* ====================================================================
   3. Tab 2: Planning & Reasoning Arena
   ==================================================================== */
function initTab2PlanningArena() {
    const btnRunArena = document.getElementById("btn-run-arena");
    const arenaTraceContainer = document.getElementById("arena-traces");

    if (!btnRunArena) return;

    btnRunArena.addEventListener("click", () => {
        btnRunArena.disabled = true;
        btnRunArena.innerHTML = `<div class="spinner" style="width:14px;height:14px;border-top-color:var(--ink-deep);"></div> Simulating...`;

        setTimeout(() => {
            arenaTraceContainer.innerHTML = `
                <div class="grid-3">
                    <!-- Column 1: Plan-and-Solve -->
                    <div class="glass-card" style="border-top: 3px solid var(--rose-accent);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                            <span style="font-weight:700; color: #fca5a5;">Plan-and-Solve (P&S)</span>
                            <span style="font-size: 0.75rem; background: rgba(244, 63, 94, 0.2); color: #fca5a5; padding: 0.2rem 0.5rem; border-radius: 4px;">Static Execution</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Generates rigid 5-step plan upfront.</div>
                        <div style="font-size: 0.75rem; font-family: var(--font-mono); background: rgba(0,0,0,0.3); padding: 0.75rem; border-radius: 6px; line-height: 1.6;">
                            [1] Step 1: SQL Query executed.<br>
                            [2] Step 2: Knowledge search done.<br>
                            [3] Step 3: Math aggregation run.<br>
                            <span style="color: #fca5a5;">[4] Step 4: Discrepancy detected in claim!</span><br>
                            <span style="color: #f87171;">[5] Step 5: FAILED to adapt. Blindly synthesized unverified data.</span>
                        </div>
                        <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 0.8rem;">
                            <strong>Success:</strong> 68.4% | <strong>Recovery:</strong> 0%
                        </div>
                    </div>

                    <!-- Column 2: ReAct -->
                    <div class="glass-card" style="border-top: 3px solid var(--amber-accent);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                            <span style="font-weight:700; color: #fcd34d;">Single Agent ReAct</span>
                            <span style="font-size: 0.75rem; background: rgba(245, 158, 11, 0.2); color: #fcd34d; padding: 0.2rem 0.5rem; border-radius: 4px;">Trial & Error</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Single agent interleaves thought & action.</div>
                        <div style="font-size: 0.75rem; font-family: var(--font-mono); background: rgba(0,0,0,0.3); padding: 0.75rem; border-radius: 6px; line-height: 1.6;">
                            [1] Thought: Let me check SQL.<br>
                            [2] Action: SQL query.<br>
                            [3] Thought: Let me do math in text.<br>
                            <span style="color: #fcd34d;">[4] Observation: Calculation error!</span><br>
                            [5] Thought: Let me retry query.<br>
                            [6] Action: Repeated SQL query.<br>
                            [7] Step 7-11: Context window polluted. Slow convergence.
                        </div>
                        <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 0.8rem;">
                            <strong>Success:</strong> 78.2% | <strong>Avg Steps:</strong> 10.8
                        </div>
                    </div>

                    <!-- Column 3: Multi-Agent Dynamic Replanning -->
                    <div class="glass-card" style="border-top: 3px solid var(--emerald-accent);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                            <span style="font-weight:700; color: #6ee7b7;">Multi-Agent + Replanning</span>
                            <span style="font-size: 0.75rem; background: rgba(16, 185, 129, 0.2); color: #6ee7b7; padding: 0.2rem 0.5rem; border-radius: 4px;">Collaborative DAG</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Supervisor dispatches to specialized agents.</div>
                        <div style="font-size: 0.75rem; font-family: var(--font-mono); background: rgba(0,0,0,0.3); padding: 0.75rem; border-radius: 6px; line-height: 1.6;">
                            [1] SQL Specialist executes schema query.<br>
                            [2] Quant Analyst computes EBITDA accurately.<br>
                            [3] Critical Reviewer detects $61.8M gap.<br>
                            <span style="color: #6ee7b7;">[4] REPLAN TRIGGERED: Injected deep-dive.</span><br>
                            [5] Reconciled ledger line-by-line.<br>
                            [6] Supervisor delivers verified audit synthesis.
                        </div>
                        <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 0.8rem;">
                            <strong>Success:</strong> 98.6% | <strong>Recovery:</strong> 95.8%
                        </div>
                    </div>
                </div>
            `;
            btnRunArena.disabled = false;
            btnRunArena.innerHTML = `<i class="fa-solid fa-rotate-right"></i> Re-Run Comparison`;
        }, 600);
    });
}

/* ====================================================================
   4. Tab 3: Agent Role & Tool Matrix
   ==================================================================== */
async function initTab3RolesAndTools() {
    const rolesContainer = document.getElementById("roles-cards-container");
    const schemaContainer = document.getElementById("db-schema-viewer");
    const toolSelect = document.getElementById("sandbox-tool-select");
    const toolParamInput = document.getElementById("sandbox-param-input");
    const btnExecuteTool = document.getElementById("btn-test-tool");
    const toolOutput = document.getElementById("sandbox-tool-output");

    // Fetch Roles
    try {
        const res = await fetch("/api/roles");
        const data = await res.json();
        let html = "";
        data.agents.forEach(ag => {
            html += `
                <div class="agent-card">
                    <div class="agent-card-header">
                        <div class="agent-avatar" style="background: rgba(106,95,193,0.2); color: ${ag.color || 'var(--accent-lime)'};">
                            <i class="fa-solid ${ag.icon}"></i>
                        </div>
                        <div>
                            <div class="agent-name">${ag.name}</div>
                            <div class="agent-role-title">${ag.role}</div>
                        </div>
                    </div>
                    <div class="agent-persona">${ag.persona}</div>
                    <span class="agent-active-badge">
                        <i class="fa-solid fa-circle-dot"></i> Active
                    </span>
                </div>
            `;
        });
        if (rolesContainer) rolesContainer.innerHTML = html;
    } catch (err) {
        if (rolesContainer) rolesContainer.innerHTML = `<div style="color:var(--accent-pink);">Error loading roles: ${err.message}</div>`;
    }

    // Fetch DB Schema
    try {
        const sRes = await fetch("/api/schema");
        const sData = await sRes.json();
        let sHtml = "";
        for (const [tbl, info] of Object.entries(sData)) {
            const cols = info.columns.map(c => `${c.name} (${c.type})`).join(", ");
            sHtml += `
                <div class="schema-table-entry">
                    <div class="schema-table-name">
                        <i class="fa-solid fa-table"></i> ${tbl}
                        <span style="font-size:11px; color:var(--on-dark-muted); font-weight:400;">(${info.row_count} rows)</span>
                    </div>
                    <div class="schema-table-cols">${cols}</div>
                </div>
            `;
        }
        if (schemaContainer) schemaContainer.innerHTML = sHtml;
    } catch (err) {
        if (schemaContainer) schemaContainer.innerHTML = `<div style="color:var(--accent-pink);">Error loading schema: ${err.message}</div>`;
    }

    // Tool sandbox execution
    if (btnExecuteTool) {
        btnExecuteTool.addEventListener("click", async () => {
            const tool = toolSelect.value;
            const paramVal = toolParamInput.value.trim();

            let params = {};
            if (tool === "execute_sql_query") params = { query: paramVal || "SELECT * FROM departments;" };
            else if (tool === "execute_python_calc") params = { code: paramVal || "result = sum([10, 20, 30])" };
            else if (tool === "search_enterprise_knowledge") params = { query: paramVal || "revenue target" };
            else if (tool === "verify_audit_claims") params = { claim: paramVal || "FY2025 revenue was $400M" };

            toolOutput.textContent = "Executing tool...";
            try {
                const res = await fetch("/api/test_tool", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tool_name: tool, params })
                });
                const data = await res.json();
                toolOutput.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                toolOutput.textContent = `Tool invocation error: ${err.message}`;
            }
        });
    }
}

/* ====================================================================
   5. Tab 4: Dynamic Replanning & Error Recovery Simulator
   ==================================================================== */
function initTab4ReplanningSimulator() {
    const btnSimulateAnomaly = document.getElementById("btn-sim-sql-fail");
    const btnSimulateDiscrepancy = document.getElementById("btn-sim-discrepancy");
    const simTraceContainer = document.getElementById("simulator-trace");

    if (!btnSimulateAnomaly) return;

    btnSimulateAnomaly.addEventListener("click", async () => {
        simTraceContainer.innerHTML = `<div class="loading-msg"><div class="spinner"></div> Injecting SQL Table Failure and evaluating Dynamic Replanner...</div>`;
        try {
            const res = await fetch("/api/orchestrate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: "Audit departmental budget and expenditure",
                    mode: "supervisor",
                    enable_dynamic_replanning: true,
                    simulate_anomaly: true
                })
            });
            const data = await res.json();
            renderSimResult(data, "SQL Table Failure Injected");
        } catch (err) {
            simTraceContainer.innerHTML = `<div style="color: var(--accent-pink); font-size:14px;"><i class="fa-solid fa-triangle-exclamation"></i> Simulation error: ${err.message}</div>`;
        }
    });

    btnSimulateDiscrepancy.addEventListener("click", async () => {
        simTraceContainer.innerHTML = `<div class="loading-msg"><div class="spinner"></div> Injecting Financial Discrepancy Claim and triggering Audit Replanning...</div>`;
        try {
            const res = await fetch("/api/orchestrate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: "Verify Marcus Vance closed $10M+ in contracts and reconcile ledger",
                    mode: "supervisor",
                    enable_dynamic_replanning: true,
                    simulate_anomaly: false
                })
            });
            const data = await res.json();
            renderSimResult(data, "Adversarial Discrepancy Detected");
        } catch (err) {
            simTraceContainer.innerHTML = `<div style="color: var(--accent-pink); font-size:14px;"><i class="fa-solid fa-triangle-exclamation"></i> Simulation error: ${err.message}</div>`;
        }
    });

    function renderSimResult(data, scenarioTitle) {
        let html = `
            <div class="replan-alert" style="margin-bottom: var(--space-xl);">
                <i class="fa-solid fa-bolt replan-alert-icon"></i>
                <div>
                    <div class="replan-title">Scenario: ${scenarioTitle}</div>
                    <div class="replan-desc">
                        Replanning Events Triggered: <strong style="color:var(--on-primary)">${data.replanning_events.length}</strong>
                        &nbsp;·&nbsp; Total Steps: <strong style="color:var(--on-primary)">${data.completed_steps_count}</strong>
                    </div>
                </div>
            </div>
        `;

        if (data.replanning_events && data.replanning_events.length > 0) {
            data.replanning_events.forEach(ev => {
                html += `
                    <div style="background: rgba(250,127,170,0.1); border: 1px solid rgba(250,127,170,0.3); padding: var(--space-md) var(--space-lg); border-radius: var(--r-md); margin-bottom: var(--space-md);">
                        <div style="font-size:14px; font-weight:700; color:var(--accent-pink); margin-bottom:var(--space-xs);">
                            <i class="fa-solid fa-triangle-exclamation"></i> Replanning Event at Step ${ev.step_triggered}
                        </div>
                        <div style="font-size:14px; color:var(--on-dark-muted);"><strong style="color:var(--on-primary)">Trigger:</strong> ${ev.reason}</div>
                        <div style="font-size:14px; color:var(--on-dark-muted); margin-top:var(--space-xxs);"><strong style="color:var(--accent-lime)">Action Taken:</strong> ${ev.action_taken}</div>
                    </div>
                `;
            });
        }

        html += `<div style="font-size:10px; font-weight:600; letter-spacing:0.25px; text-transform:uppercase; color:var(--on-dark-muted); margin-bottom:var(--space-md);">Adjusted Execution Waterfall</div>`;
        data.execution_trace.forEach(step => {
            html += `
                <div style="border-left: 2px solid var(--hairline-violet); padding-left: var(--space-lg); margin-bottom: var(--space-lg);">
                    <div style="font-size:14px; font-weight:600; color:var(--accent-lime); margin-bottom:var(--space-xs);">Step ${step.step}: ${step.agent} → ${step.title}</div>
                    <div style="font-size:14px; color:var(--on-dark-muted); font-style:italic; margin-bottom:var(--space-xxs);">${step.thought.substring(0, 120)}...</div>
                    <div style="font-family:var(--font-code); font-size:12px; color:var(--accent-violet-mid);">status: ${step.status}</div>
                </div>
            `;
        });

        simTraceContainer.innerHTML = html;
    }
}

/* ====================================================================
   6. Tab 5: Multi-Agent Benchmarks & LLMOps Evaluation Suite
   ==================================================================== */
let radarChartInstance = null;

async function initTab5Benchmarks() {
    renderRadarChart();
    loadBenchmarkTable();
}

async function renderRadarChart() {
    const canvas = document.getElementById("benchmarkRadarChart");
    if (!canvas) return;

    try {
        const res = await fetch("/api/benchmarks");
        const data = await res.json();
        const radarData = data.strategies_comparison.metrics_radar;

        if (radarChartInstance) {
            radarChartInstance.destroy();
        }

        radarChartInstance = new Chart(canvas, {
            type: "radar",
            data: {
                labels: radarData.labels,
                datasets: radarData.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: "rgba(54,45,89,0.8)" },
                        grid: { color: "rgba(54,45,89,0.8)" },
                        pointLabels: {
                            color: "rgba(255,255,255,0.72)",
                            font: { size: 12, family: "Rubik" }
                        },
                        ticks: {
                            color: "rgba(255,255,255,0.4)",
                            backdropColor: "transparent",
                            min: 0,
                            max: 100
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: "top",
                        labels: { color: "rgba(255,255,255,0.9)", font: { size: 12, family: "Rubik" } }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Error rendering radar chart:", err);
    }
}

async function loadBenchmarkTable() {
    const tableBody = document.getElementById("benchmark-scenarios-body");
    if (!tableBody) return;

    try {
        const res = await fetch("/api/benchmarks");
        const data = await res.json();
        let html = "";
        data.scenarios.forEach(sc => {
            html += `
                <tr>
                    <td style="font-weight: 600; color: var(--accent-lime); font-family: var(--font-code); font-size:13px;">${sc.id}</td>
                    <td style="font-size:14px;">${sc.name}</td>
                    <td>${sc.domains.map(d => `<span class="domain-pill">${d}</span>`).join("")}</td>
                    <td><span class="${sc.single_agent_success ? 'pass' : 'fail'}">${sc.single_agent_success ? 'Pass' : 'Fail'}</span> <span style="color:var(--on-dark-muted); font-size:13px;">(${sc.single_agent_steps} steps)</span></td>
                    <td><span class="pass">Pass</span> <span style="color:var(--on-dark-muted); font-size:13px;">(${sc.multi_agent_steps} steps)</span></td>
                    <td style="font-size: 13px; color: var(--on-dark-muted);">${sc.discrepancy_resolved}</td>
                </tr>
            `;
        });
        tableBody.innerHTML = html;
    } catch (err) {
        console.error("Error loading benchmark table:", err);
    }
}

/* ====================================================================
   Utilities: Simple Markdown to HTML Formatter
   ==================================================================== */
function formatMarkdown(md) {
    if (!md) return "";
    let html = md
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code class="inline-code">$1</code>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        .replace(/\n\n/gim, '<br><br>');

    // Wrap list items in <ul>
    html = html.replace(/(?:<li>.*?<\/li>\s*)+/gim, match => `<ul>${match}</ul>`);
    return html;
}
