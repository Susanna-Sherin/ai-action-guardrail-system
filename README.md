# Action Guardrail

A pre-execution policy engine for AI agent tool calls. Evaluates every
tool call an agent wants to make against a declarative YAML ruleset and
routes it to `block`, `require_hitl`, or `log_and_allow` before it executes.

Built for Aivar Innovations' Agentic AI Task (PS-3.1).

## Status
- [x] Phase 0 — project skeleton, dependencies, env config
- [ ] Phase 1 — policy engine core
- [ ] Phase 2 — agent + real LLM integration
- [ ] Phase 3 — FastAPI backend
- [ ] Phase 4 — persistence layer
- [ ] Phase 5 — simulation harness
- [ ] Phase 6 — frontend dashboard
- [ ] Phase 7 — containerization & deployment
- [ ] Phase 8 — polish, concurrency proof, explanation prep

## Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your LLM_PROVIDER + API key
```

## Run (once Phase 3 is done)
```bash
uvicorn backend.main:app --reload
```
