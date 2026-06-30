// DeepPilot Interactive UI Controller
const API_BASE = "http://127.0.0.1:8000/api";
let currentTaskId = null;
let pollInterval = null;

const steps = ["planner", "researcher", "coder", "tester", "debugger", "reflector"];

function setPrompt(text) {
    document.getElementById("taskInput").value = text;
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));
    
    event.currentTarget.classList.add("active");
    document.getElementById(tabId).classList.add("active");
}

function updateStatusBadge(status) {
    const badge = document.getElementById("currentStatusText");
    badge.className = `status-label ${status}`;
    badge.textContent = `Status: ${status.toUpperCase()}`;
}

function updateStepper(activeStepIndex, isComplete = false) {
    steps.forEach((step, idx) => {
        const el = document.getElementById(`step-${step}`);
        el.classList.remove("active", "completed");
        
        if (isComplete || idx < activeStepIndex) {
            el.classList.add("completed");
        } else if (idx === activeStepIndex && !isComplete) {
            el.classList.add("active");
        }
    });
}

document.getElementById("startBtn").addEventListener("click", async () => {
    const goal = document.getElementById("taskInput").value.trim();
    if (!goal) {
        alert("Please describe an engineering task first.");
        return;
    }

    const startBtn = document.getElementById("startBtn");
    startBtn.disabled = true;
    startBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Swarm Active...`;
    
    updateStatusBadge("running");
    updateStepper(0);

    try {
        const response = await fetch(`${API_BASE}/workflow/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ goal: goal })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentTaskId = data.task_id;
            startPolling(currentTaskId);
        } else {
            alert("Failed to start workflow. Check uvicorn API console.");
            resetStartButton();
        }
    } catch (e) {
        alert("Error connecting to API server at " + API_BASE);
        resetStartButton();
    }
});

function resetStartButton() {
    const startBtn = document.getElementById("startBtn");
    startBtn.disabled = false;
    startBtn.innerHTML = `<i class="fa-solid fa-rocket"></i> Launch Autonomous Swarm`;
}

function startPolling(taskId) {
    if (pollInterval) clearInterval(pollInterval);
    
    let stepCycle = 0;
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE}/workflow/${taskId}/status`);
            if (res.ok) {
                const data = await res.json();
                const status = data.status;
                
                if (status === "running") {
                    stepCycle = (stepCycle + 1) % steps.length;
                    updateStepper(stepCycle);
                } else if (status === "completed") {
                    clearInterval(pollInterval);
                    updateStatusBadge("completed");
                    updateStepper(steps.length - 1, true);
                    renderResults(data.result);
                    resetStartButton();
                } else if (status === "failed") {
                    clearInterval(pollInterval);
                    updateStatusBadge("failed");
                    document.getElementById("testOutput").textContent = `Workflow Execution Failed:\n${data.error}`;
                    resetStartButton();
                }
            }
        } catch (e) {
            console.error("Polling error:", e);
        }
    }, 2500);
}

function renderResults(result) {
    // 1. Render Plan
    if (result.plan && result.plan.steps) {
        document.getElementById("planEmpty").classList.add("hidden");
        const container = document.getElementById("planContainer");
        container.classList.remove("hidden");
        container.innerHTML = result.plan.steps.map(s => `
            <div class="plan-step-card">
                <div class="plan-step-header">
                    <span>Step ${s.step_number}: ${s.component}</span>
                </div>
                <p>${s.description}</p>
            </div>
        `).join("");
    }

    // 2. Render Generated Code
    if (result.generated_code) {
        document.getElementById("codeBlock").textContent = result.generated_code;
    }

    // 3. Render Test Results
    if (result.test_results) {
        document.getElementById("testOutput").textContent = result.test_results;
    }

    // 4. Render Reflection
    if (result.reflection) {
        const refContainer = document.getElementById("reflectionContainer");
        const isCorrect = result.reflection.is_correct;
        refContainer.innerHTML = `
            <div class="plan-step-card" style="border-left-color: ${isCorrect ? '#10b981' : '#ef4444'}">
                <div class="plan-step-header">
                    <span>Evaluation Status: ${isCorrect ? '✅ PASSED CRITIQUE' : '⚠️ IMPROVEMENTS NEEDED'}</span>
                </div>
                <p style="margin-top: 8px;"><strong>Critique:</strong> ${result.reflection.critique || 'No critique provided.'}</p>
            </div>
        `;
    }
}

function copyCode() {
    const codeText = document.getElementById("codeBlock").textContent;
    navigator.clipboard.writeText(codeText).then(() => {
        alert("Code copied to clipboard!");
    });
}

async function searchMemory() {
    const query = document.getElementById("memoryQuery").value.trim();
    if (!query) return;

    try {
        const res = await fetch(`${API_BASE}/memory/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, collection: "semantic_memory", k: 3 })
        });
        if (res.ok) {
            const data = await res.json();
            const resultsDiv = document.getElementById("memoryResults");
            if (data.results && data.results.documents && data.results.documents[0].length > 0) {
                resultsDiv.innerHTML = data.results.documents[0].map(doc => `
                    <div class="plan-step-card">
                        <p>${doc}</p>
                    </div>
                `).join("");
            } else {
                resultsDiv.innerHTML = `<p class="hint-text">No matching semantic memory patterns found.</p>`;
            }
        }
    } catch (e) {
        alert("Memory search failed.");
    }
}
