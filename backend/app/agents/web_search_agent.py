import logging
from typing import Any, Dict
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from tavily import AsyncTavilyClient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models and Dependencies
@dataclass
class SearchDataclass:
    max_results: int = 5
    todays_date: str = datetime.now().strftime("%Y-%m-%d")

# Initialize model and Tavily client
model = GeminiModel('gemini-1.5-flash')
tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Create agent
web_search_agent = Agent(
    model=model,
    deps_type=SearchDataclass,
    result_type=str,
    system_prompt=(
        "You are a Research News Assistant. For every query:"
        "\n1. ALWAYS use get_search to find current information"
        "\n2. Format results clearly with markdown"
        "\n3. Include dates and sources"
    )
)

@web_search_agent.tool
async def get_search(ctx: RunContext[SearchDataclass], query: str, query_number: int) -> Dict[str, Any]:
    """Perform a search using Tavily API"""
    try:
        logger.info(f"Starting search {query_number} for: {query}")
        results = await tavily_client.get_search_context(
            query=query,
            max_results=ctx.deps.max_results
        )
        
        if not results:
            return {"error": "No results found"}
            
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return {"error": str(e)}

@web_search_agent.system_prompt
async def add_current_date(ctx: RunContext[SearchDataclass]) -> str:
    """Add current date to system prompt"""
    return (
        f"You're a Research News Assistant specialized in finding latest developments. "
        f"When given a query:"
        f"\n1. Use get_search to find current information (use query_number 1-3 for different searches)"
        f"\n2. Format results with clear markdown"
        f"\n3. Include today's date {ctx.deps.todays_date}"
        f"\n4. Focus on recent and relevant information"
        f"\n5. Combine results into a coherent summary"
    )

async def format_search_results(results: Dict[str, Any]) -> str:
    """Format search results into markdown"""
    if "error" in results:
        return f"Error: {results['error']}"
        
    try:
        formatted = ["### Search Results\n"]
        for result in results.get("results", []):
            title = result.get("title", "No title")
            url = result.get("url", "#")
            snippet = result.get("snippet", "No description available")
            
            formatted.extend([
                f"#### {title}",
                f"[Source]({url})",
                f"{snippet}\n"
            ])
            
        return "\n".join(formatted)
    except Exception as e:
        logger.error(f"Error formatting results: {e}")
        return "Error formatting search results"

# Initialize with default dependencies
default_deps = SearchDataclass()