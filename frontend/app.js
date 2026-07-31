const BASE_URL = "";

/* -----------------------------
   Check Backend Health
------------------------------*/
async function checkHealth() {
    const health = document.getElementById("healthStatus");

    try {
        const response = await fetch(`${BASE_URL}/health`);
        const data = await response.json();

        health.innerHTML =
            `<span class="success">🟢 ${data.status.toUpperCase()}</span>`;

    } catch (error) {
        health.innerHTML =
            `<span class="error">🔴 Backend Offline</span>`;
    }
}

/* -----------------------------
   Execute Agent
------------------------------*/
async function executeAgent() {

    const prompt = document.getElementById("promptInput").value.trim();
    const dryRun = document.getElementById("dryRun").checked;

    if (prompt === "") {
        alert("Please enter a prompt.");
        return;
    }

    document.getElementById("toolCall").textContent = "Generating...";
    document.getElementById("decision").textContent = "Evaluating...";
    document.getElementById("execution").textContent = "Waiting...";

    try {

        const response = await fetch(`${BASE_URL}/agent/request`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                prompt: prompt,
                dry_run: dryRun
            })

        });

        const data = await response.json();

        /* Tool Call */

        document.getElementById("toolCall").textContent =
            JSON.stringify(data.tool_call, null, 4);

        /* Decision */

        document.getElementById("decision").innerHTML = `
            <b>Outcome:</b> ${data.decision.outcome}<br>
            <b>Matched Rule:</b> ${data.decision.matched_rule ?? "None"}<br>
            <b>Reason:</b><br>${data.decision.reason}
        `;

        /* Execution */

        document.getElementById("execution").innerHTML = `
            <b>Status:</b> ${data.execution.status}<br>
            <b>Message:</b> ${data.execution.message}
        `;

        loadAuditLogs();
        loadHitlQueue();
        loadStats();

        checkHealth();

    }

    catch (error) {

        alert("Backend Error!");

        console.error(error);

    }

}

/* -----------------------------
   Audit Logs
------------------------------*/

async function loadAuditLogs() {

    const table = document.getElementById("auditTable");

    table.innerHTML = "";

    const response = await fetch(`${BASE_URL}/audit`);

    const logs = await response.json();

    logs.forEach(log => {

        table.innerHTML += `

        <tr>

            <td>${log.id}</td>

            <td>${log.prompt}</td>

            <td>${log.tool}</td>

            <td>${log.decision}</td>

            <td>${log.matched_rule ?? "-"}</td>

            <td>${new Date(log.timestamp).toLocaleString()}</td>

        </tr>

        `;

    });

}

/* -----------------------------
   HITL Queue
------------------------------*/

async function loadHitlQueue() {

    const table = document.getElementById("hitlTable");

    table.innerHTML = "";

    const queue = await fetch(`${BASE_URL}/hitl`);

    const requests = await queue.json();

    requests.forEach(req => {

        table.innerHTML += `

        <tr>

            <td>${req.id}</td>

            <td>${req.prompt}</td>

            <td>${req.tool}</td>

            <td>

                <button
                    class="approve-btn"
                    onclick="approve(${req.id})">

                    Approve

                </button>

                <button
                    class="reject-btn"
                    onclick="rejectRequest(${req.id})">

                    Reject

                </button>

            </td>

        </tr>

        `;

    });

}

/* -----------------------------
   Approve
------------------------------*/

async function approve(id) {

    await fetch(`${BASE_URL}/hitl/${id}/approve`, {

        method: "POST"

    });

    loadHitlQueue();

}

/* -----------------------------
   Reject
------------------------------*/

async function rejectRequest(id) {

    await fetch(`${BASE_URL}/hitl/${id}/reject`, {

        method: "POST"

    });

    loadHitlQueue();

}

async function loadStats(){

    const response=await fetch(`${BASE_URL}/stats`);

    const stats=await response.json();

    document.getElementById("totalRequests").textContent=stats.total;

    document.getElementById("blockedCount").textContent=stats.blocked;

    document.getElementById("allowedCount").textContent=stats.allowed;

    document.getElementById("pendingCount").textContent=stats.pending;

}
/* -----------------------------
   Events
------------------------------*/

document
    .getElementById("executeBtn")
    .addEventListener("click", executeAgent);

checkHealth();

loadAuditLogs();

loadHitlQueue();

loadStats();