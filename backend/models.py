from pydantic import BaseModel


class AgentRequest(BaseModel):
    prompt: str
    dry_run: bool = False


class AgentResponse(BaseModel):
    tool_call: dict
    decision: dict
    execution: dict