from fastapi import FastAPI, HTTPException
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import os
from dotenv import load_dotenv
from services.arxiv_service import search_arxiv
from services.google_scholar_service import search_google_scholar
from services.ai_agent import research_agent
from pydantic import BaseModel

class AgentRequest(BaseModel):
    prompt: str

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Initialize the Groq LLM Agent (already done in ai_agent.py)
# research_agent is already imported

@app.get("/")
def read_root():
    return {"message": "Academic Research Assistant API"}

@app.get("/search/arxiv")
def search_arxiv_endpoint(query: str, max_results: int = 5):
    """
    Endpoint to search for papers on ArXiv.
    """
    try:
        papers = search_arxiv(query, max_results)
        return {"source": "arxiv", "results": papers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/run")
async def run_agent(request: AgentRequest):
    """
    Endpoint to interact with the AI agent.
    """
    try:
        result = await research_agent.run(request.prompt)
        return {"response": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))