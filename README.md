# 🛡️ Action Guardrail: Enterprise AI Action Policy Enforcement

## Overview

Action Guardrail is an AI governance layer that evaluates AI agent actions **before execution**.

The system intercepts AI-generated tool calls and applies declarative policies to decide whether an action should:

- ✅ Allow execution
- ❌ Block execution
- ⏸️ Require Human-in-the-Loop (HITL) approval
- 📝 Log the action for auditing

It provides a safety layer between autonomous AI agents and real-world tools.

---

# Architecture
             User
              |
              |
      Natural Language Prompt
              |
              ↓
        AI Agent (Gemini)
              |
              |
    Structured Tool Action
              |
              ↓
    Action Guardrail Engine
              |
    -------------------------
    |          |            |
    ↓          ↓            ↓
  ALLOW      BLOCK        HITL
    |          |            |
Execute     Reject     Human Review
                           |
                     Approve / Reject


              |
              ↓

          Audit Database


---

# Features

## 🔐 Policy Enforcement Engine

- YAML-based declarative policies
- Supports:
  - block
  - require_hitl
  - log_and_allow

---

## 🤖 LLM Agent Integration

Uses Google Gemini to convert user requests into structured tool actions.

Example:

User:
Delete 500 customer records

Agent generates:

```json
{
  "tool": "database_delete",
  "records": 500
}
```

The guardrail evaluates this before execution.

⛔ Action Blocking

Dangerous actions are automatically rejected.

Example:

Delete 5000 database records

Result:

BLOCKED
👤 Human-in-the-Loop Approval

Sensitive actions can be paused for human review.

Example:

Send email to external recipient

Result:

WAITING_FOR_APPROVAL

Human can:

Approve
Reject
📊 Audit Logging

Every decision is stored:

Action requested
Tool selected
Policy matched
Decision
Timestamp
🖥️ Dashboard

Frontend provides:

System health monitoring
Audit history
HITL queue
Execution results
🐳 Docker Support

Fully containerized using:

Docker
Docker Compose
Technology Stack
Backend
Python
FastAPI
SQLAlchemy
SQLite
AI
Google Gemini API
Policy Engine
YAML Rules
SimpleEval
Frontend
HTML
CSS
JavaScript
Deployment
Docker
Docker Compose
Project Structure
action-guardrail/

│
├── backend/
│   ├── agent.py
│   ├── policy_engine.py
│   ├── policy.yaml
│   ├── models.py
│   ├── db.py
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── tests/
│
├── data/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
Running Locally
Prerequisites

Install:

Python 3.9+
Docker
Docker Compose
Environment Setup

Create environment file:

cp .env.example .env

Add your Gemini API key:

GEMINI_API_KEY=<your_key>
Start Application

Build and run:

docker compose up --build

Application:

http://localhost:8000

Swagger API:

http://localhost:8000/docs
API Endpoints
Endpoint	Description
GET /health	Backend health check
POST /agent/request	Submit AI action request
GET /audit	View audit logs
GET /hitl	View pending approvals
POST /hitl/{id}/approve	Approve action
POST /hitl/{id}/reject	Reject action
Example Workflow
Allowed Action

Request:

Delete 5 customer records

Decision:

ALLOW
Blocked Action

Request:

Delete 5000 customer records

Decision:

BLOCK
HITL Action

Request:

Send confidential email externally

Decision:

REQUIRES HUMAN APPROVAL
Testing

Run:

pytest tests/

Tests cover:

Policy evaluation
Agent behavior
Guardrail scenarios
Future Improvements
Authentication and authorization
Real tool execution connectors
Cloud deployment
Advanced monitoring
Dynamic policy updates
Multi-agent governance

