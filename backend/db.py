import json
from backend.tools import execute_tool
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

from backend.config import DB_PATH
from sqlalchemy import func

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    prompt = Column(String)
    tool = Column(String)

    decision = Column(String)
    matched_rule = Column(String)
    reason = Column(String)


class HITLQueue(Base):
    __tablename__ = "hitl_queue"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    prompt = Column(String)
    tool = Column(String)


    tool_call = Column(String) 

    status = Column(String, default="Pending")


def create_database():
    Base.metadata.create_all(bind=engine)


def save_audit_log(prompt, tool, decision, matched_rule, reason):

    db = SessionLocal()

    log = AuditLog(
        prompt=prompt,
        tool=tool,
        decision=decision,
        matched_rule=matched_rule,
        reason=reason,
    )

    db.add(log)
    db.commit()
    db.close()


def add_hitl_request(prompt, tool, tool_call):

    db = SessionLocal()

    request = HITLQueue(
        prompt=prompt,
        tool=tool,
        tool_call=json.dumps(tool_call),
        status="Pending",
    )

    db.add(request)
    db.commit()
    db.close()


def get_all_audit_logs():

    db = SessionLocal()

    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).all()

    result = []

    for log in logs:
        result.append({
            "id": log.id,
            "timestamp": str(log.timestamp),
            "prompt": log.prompt,
            "tool": log.tool,
            "decision": log.decision,
            "matched_rule": log.matched_rule,
            "reason": log.reason
        })

    db.close()

    return result


def get_pending_hitl():

    db = SessionLocal()

    requests = db.query(HITLQueue).filter(
        HITLQueue.status == "Pending"
    ).all()

    result = []

    for r in requests:

        result.append({
            "id": r.id,
            "timestamp": str(r.timestamp),
            "prompt": r.prompt,
            "tool": r.tool,
            "status": r.status
        })

    db.close()

    return result

def approve_hitl(request_id):

    db = SessionLocal()

    request = db.query(HITLQueue).filter(
        HITLQueue.id == request_id
    ).first()

    if not request:
        db.close()
        return {
            "status": "error",
            "message": "Request not found"
        }

    # Convert JSON string back to dictionary
    tool_call = json.loads(request.tool_call)

    # Execute the original tool
    execution_result = execute_tool(tool_call)

    # Mark request as approved
    request.status = "Approved"

    db.commit()
    db.close()

    return execution_result

def approve_hitl(request_id):

    print("STEP 1 - approve_hitl called")

    db = SessionLocal()

    request = db.query(HITLQueue).filter(
        HITLQueue.id == request_id
    ).first()

    if not request:
        print("STEP 2 - Request not found")
        db.close()
        return {
            "status": "error",
            "message": "Request not found"
        }

    print("STEP 3 - Request found")
    print(request.tool_call)

    tool_call = json.loads(request.tool_call)

    print("STEP 4 - JSON loaded")
    print(tool_call)

    execution_result = execute_tool(tool_call)

    print("STEP 5 - Tool executed")
    print(execution_result)

    request.status = "Approved"

    db.commit()
    db.close()

    print("STEP 6 - Returning result")

    return execution_result
def get_statistics():
    """
    Returns dashboard statistics.
    """

    db = SessionLocal()

    total = db.query(AuditLog).count()

    blocked = db.query(AuditLog).filter(
        AuditLog.decision == "block"
    ).count()

    allowed = db.query(AuditLog).filter(
        AuditLog.decision == "log_and_allow"
    ).count()

    hitl = db.query(AuditLog).filter(
        AuditLog.decision == "require_hitl"
    ).count()

    pending = db.query(HITLQueue).filter(
        HITLQueue.status == "Pending"
    ).count()

    db.close()

    return {
        "total": total,
        "blocked": blocked,
        "allowed": allowed,
        "hitl": hitl,
        "pending": pending,
    }
def get_all_audit_logs():

    db = SessionLocal()

    logs = db.query(AuditLog).order_by(
        AuditLog.id.desc()
    ).all()

    result = []

    for log in logs:

        result.append({
            "id": log.id,
            "timestamp": log.timestamp,
            "prompt": log.prompt,
            "tool": log.tool,
            "decision": log.decision,
            "matched_rule": log.matched_rule,
            "reason": log.reason
        })

    db.close()

    return result


def get_pending_hitl():

    db = SessionLocal()

    requests = db.query(HITLQueue).filter(
        HITLQueue.status == "Pending"
    ).all()

    result = []

    for r in requests:

        result.append({
            "id": r.id,
            "timestamp": r.timestamp,
            "prompt": r.prompt,
            "tool": r.tool,
            "status": r.status
        })

    db.close()

    return result


def approve_hitl(request_id):

    db = SessionLocal()

    request = db.query(HITLQueue).filter(
        HITLQueue.id == request_id
    ).first()

    if not request:
        db.close()
        return {
            "status": "error",
            "message": "Request not found"
        }

    tool_call = json.loads(request.tool_call)

    execution_result = execute_tool(tool_call)

    request.status = "Approved"

    db.commit()
    db.close()

    return execution_result

def reject_hitl(request_id: int):

    db = SessionLocal()

    request = db.query(HITLQueue).filter(
        HITLQueue.id == request_id
    ).first()

    if request:
        request.status = "Rejected"

    db.commit()
    db.close()