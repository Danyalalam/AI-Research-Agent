from typing import Dict, List
import os
import logging
from tavily import TavilyClient
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TavilyService:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        self.client = TavilyClient(api_key=api_key)
        
    async def search(self, query: str, max_results: int = 3) -> List[Dict]:
        try:
            logger.info(f"Performing Tavily search for: {query}")
            response = self.client.search(
                query=f"{query} latest news {datetime.now().strftime('%Y-%m-%d')}",
                search_depth="advanced",
                max_results=max_results
            )
            logger.info("Tavily search completed successfully")
            return response.get("results", [])
        except Exception as e:
            logger.error(f"Tavily search error: {e}", exc_info=True)
            raise