from pydantic import BaseModel

class AgentRequest(BaseModel):
    prompt: str