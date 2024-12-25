from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.agents.research_agent import research_agent, search_papers_tool
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Research Assistant API"}

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    Endpoint to interact with the AI agent for paper search.
    """
    try:
        logger.info(f"Agent received prompt: {request.prompt}")
        result = await research_agent.run(request.prompt)
        logger.info("Agent processed the prompt successfully")
        return {"response": result.data}
    except Exception as e:
        logger.error(f"Error in /agent/run: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Agent processing failed.")