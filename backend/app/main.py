from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
import logging
import os  # Add this import

from app.agents.research_agent import research_agent, search_papers_tool
from app.agents.web_search_agent import web_search_agent
from app.services.plagiarism_checker import AIDetector  # Add this import
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

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

class PlagiarismRequest(BaseModel):
    text: str

# Response Models
class AgentResponse(BaseModel):
    response: str

class WebSearchResponse(BaseModel):
    response: str

class PlagiarismResponse(BaseModel):
    success: bool
    ai_probability: float = None
    human_probability: float = None
    scan_id: str = None
    total_words: int = None
    error: str = None

# Initialize AIDetector using environment variables for security
EMAIL_ADDRESS = os.getenv('COPYLEAKS_EMAIL')
KEY = os.getenv('COPYLEAKS_KEY')

if not EMAIL_ADDRESS or not KEY:
    logger.error("Copyleaks credentials are not set.")
    raise Exception("Copyleaks credentials are missing.")

aidetector = AIDetector(email=EMAIL_ADDRESS, api_key=KEY)

# Mount the frontend directory
current_file = Path(__file__).resolve()
current_dir = current_file.parent  # backend/app/
root_dir = current_dir.parent.parent  # AI RESEARCH AGENT/
frontend_dir = root_dir / "frontend"

if not frontend_dir.is_dir():
    logger.error(f"Frontend directory not found at {frontend_dir}")
    raise RuntimeError(f"Frontend directory does not exist at {frontend_dir}")

# Mount the frontend directory for static files
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = frontend_dir / "index.html"
    if not index_path.is_file():
        logger.error(f"index.html not found at {index_path}")
        raise HTTPException(status_code=404, detail="index.html not found.")
    with index_path.open("r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

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

# Plagiarism Check Endpoint
@app.post("/agent/plagiarism-check", response_model=PlagiarismResponse)
async def run_plagiarism_check(request: PlagiarismRequest):
    """
    Endpoint to perform plagiarism check using Copyleaks Writer Detector.
    """
    try:
        input_text = request.text.strip()
        logger.info(f"Plagiarism Check received text: {input_text[:50]}...")

        if not input_text:
            logger.error("No text provided for plagiarism check.")
            return PlagiarismResponse(success=False, error="No text provided for plagiarism check.")

        result = aidetector.detect_ai(input_text)
        logger.info("Plagiarism Check processed the text successfully")

        if result.get("success"):
            return PlagiarismResponse(
                success=True,
                ai_probability=result.get("ai_probability"),
                human_probability=result.get("human_probability"),
                scan_id=result.get("scan_id"),
                total_words=result.get("total_words")
            )
        else:
            return PlagiarismResponse(
                success=False,
                error=result.get("error")
            )
    except Exception as e:
        logger.error(f"Error in /agent/plagiarism-check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))