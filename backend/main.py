from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.agent import generate_tool_call
from backend.policy_engine import load_policy, evaluate_action
from backend.config import POLICY_FILE
from backend.logging_config import logger
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.db import (
    create_database,
    save_audit_log,
    add_hitl_request,
    get_statistics,
    get_all_audit_logs,
    get_pending_hitl,
    approve_hitl,
    reject_hitl,
)
from backend.tools import execute_tool
from backend.models import AgentRequest

app = FastAPI(
    title="Action Guardrail",
    version="1.0"
)

frontend_path = Path("frontend")

app.mount(
    "/frontend",
    StaticFiles(directory=frontend_path),
    name="frontend"
)

app.add_middleware(
    CORSMiddleware,allow_origins=["http://127.0.0.1:5500","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_database()

policy = load_policy(POLICY_FILE)

@app.get("/stats")
def stats():

    return get_statistics()

@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/agent/request")
def agent_request(request: AgentRequest):
    try:
        # Log incoming prompt
        logger.info(f"Received prompt: {request.prompt}")

        tool_call = generate_tool_call(request.prompt)

        decision = evaluate_action(tool_call, policy)

        # Log decision outcome
        logger.info(
            f"Policy decision: {decision['outcome']} for tool {tool_call['tool']}")

        save_audit_log(
            prompt=request.prompt,
            tool=tool_call["tool"],
            decision=decision["outcome"],
            matched_rule=decision["matched_rule"],
            reason=decision["reason"],
        )

        if decision["outcome"] == "require_hitl":
            add_hitl_request(
                prompt=request.prompt,
                tool=tool_call["tool"],
                tool_call=tool_call
            )
            return {
                "tool_call": tool_call,
                "decision": decision,
                "execution": {
                    "status": "WAITING_FOR_APPROVAL",
                    "message": "Request added to HITL queue."
                }
            }

        if decision["outcome"] == "block":
            return {
                "tool_call": tool_call,
                "decision": decision,
                "execution": {
                    "status": "BLOCKED",
                    "message": "Policy blocked execution."
                }
            }

        if request.dry_run:
            logger.info(f"Dry run enabled - skipping execution for prompt: {request.prompt}")
            return {
                "tool_call": tool_call,
                "decision": decision,
                "execution": {
                    "status": "DRY_RUN",
                    "message": "Execution skipped due to dry-run mode."
                }
            }

        result = execute_tool(tool_call)

        return {
            "tool_call": tool_call,
            "decision": decision,
            "execution": result
        }

    except Exception as e:
        logger.exception("Error processing agent request")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/audit")
def get_audit():
    return get_all_audit_logs()


@app.get("/hitl")
def get_hitl():
    return get_pending_hitl()


@app.post("/hitl/{request_id}/approve")
def approve(request_id: int):

    result = approve_hitl(request_id)

    return {
        "message": "Approved",
        "execution": result
    }


@app.post("/hitl/{request_id}/reject")
def reject(request_id: int):
    reject_hitl(request_id)
    return {"message": "Rejected"}