import os
import logging
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from tavily import AsyncTavilyClient
from .arxiv_service import search_arxiv
from dotenv import load_dotenv
import asyncio
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the Tavily Client
tavily_client = AsyncTavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Initialize the Groq LLM Model
model = GroqModel('llama-3.3-70b-versatile')

# Initialize the Agent without dependencies
research_agent = Agent(
    model=model,
    result_type=str,
    system_prompt=(
        "You are an Academic Research Assistant. Use the available tools to help users find and summarize research papers based on their queries."
    ),
)

# Rate Limiter Decorator
def rate_limit(max_calls: int, period: float):
    """Simple rate limiter decorator."""
    semaphore = asyncio.Semaphore(max_calls)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)
        return wrapper
    return decorator

@research_agent.tool
async def search_arxiv_tool(ctx: RunContext, query: str) -> str:
    """Search for papers on ArXiv based on the query."""
    try:
        logger.info(f"Received ArXiv search query: {query}")
        papers = search_arxiv(query, max_results=5)
        if not papers:
            response = "No papers found on ArXiv for your query."
            logger.info(response)
            return response
        response = "ArXiv Results:\n"
        for paper in papers:
            response += f"Title: {paper['title']}\nAuthors: {', '.join(paper['authors'])}\nURL: {paper['url']}\n\n"
        logger.info("ArXiv search successful.")
        return response
    except Exception as e:
        logger.error(f"Error in ArXiv search tool: {e}")
        return f"An error occurred while searching ArXiv: {e}"

@research_agent.tool
@rate_limit(max_calls=5, period=60)  # 5 calls per 60 seconds
async def web_search_tool(ctx: RunContext, query: str, query_number: int) -> dict:
    """Perform a web search using Tavily with rate limiting."""
    try:
        logger.info(f"Performing web search {query_number}: {query}")
        response = await tavily_client.search(query, max_results=3)
        results = response.get('results', [])
        search_results = []
        for result in results:
            search_results.append({
                'title': result['title'],
                'content': result['content']
            })
        logger.info(f"Web search {query_number} successful.")
        return {'results': search_results}
    except Exception as e:
        logger.error(f"Error in web search tool: {e}")
        return {'results': [], 'error': str(e)}

@research_agent.tool
async def summarize_tool(ctx: RunContext, text: str) -> str:
    """Summarize the provided text."""
    try:
        logger.info("Received text for summarization.")
        prompt = f"Summarize the following text:\n\n{text}"
        
        # Use the Agent's run method to perform summarization
        summary = await research_agent.run(prompt)
        
        logger.info("Summarization successful.")
        return summary
    except Exception as e:
        logger.error(f"Error in summarization tool: {e}")
        return f"An error occurred while summarizing the text: {e}"