from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.agents.research_agent import research_agent, search_papers_tool
from app.agents.web_search_agent import web_search_agent
from datetime import datetime
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for Web Search
@dataclass
class SearchDataclass:
    max_results: int = 5
    todays_date: str = datetime.now().strftime("%Y-%m-%d")

# Dependency for Paper Search (if different dependencies are needed)
@dataclass
class PaperSearchDataclass:
    max_results: int = 5
    todays_date: str = datetime.now().strftime("%Y-%m-%d")

# Request Models
class AgentRequest(BaseModel):
    prompt: str

class WebSearchRequest(BaseModel):
    prompt: str

# Response Models
class AgentResponse(BaseModel):
    response: str

class WebSearchResponse(BaseModel):
    response: str

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Research Assistant API"}

# Paper Search Endpoint
@app.post("/agent/paper-search", response_model=AgentResponse)
async def run_paper_search(request: AgentRequest):
    """
    Endpoint to interact with the AI agent for paper search.
    """
    try:
        logger.info(f"Paper Search received prompt: {request.prompt}")
        deps = PaperSearchDataclass(
            max_results=5,
            todays_date=datetime.now().strftime("%Y-%m-%d")
        )
        result = await research_agent.run(request.prompt, deps=deps)
        logger.info("Paper Search processed the prompt successfully")
        return {"response": result.data if hasattr(result, 'data') else str(result)}
    except Exception as e:
        logger.error(f"Error in /agent/paper-search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Web Search Endpoint
@app.post("/agent/web-search", response_model=WebSearchResponse)
async def run_web_search(request: WebSearchRequest):
    """
    Endpoint to perform web search.
    """
    try:
        logger.info(f"Web Search received prompt: {request.prompt}")
        deps = SearchDataclass(
            max_results=5,
            todays_date=datetime.now().strftime("%Y-%m-%d")
        )
        result = await web_search_agent.run(request.prompt, deps=deps)
        logger.info("Web Search processed the prompt successfully")
        return {"response": result.data if hasattr(result, 'data') else str(result)}
    except Exception as e:
        logger.error(f"Error in /agent/web-search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))