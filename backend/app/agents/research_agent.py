import logging
from typing import List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from app.services.arxiv_service import search_arxiv, Paper
import re
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = GeminiModel('gemini-1.5-flash')

model = GeminiModel('gemini-1.5-flash')

# Update system prompt
research_agent = Agent(
    model=model,
    result_type=str,
    system_prompt=(
        "You are an Academic Research Assistant specialized in searching and analyzing research papers. "
        "When given a query, you will:"
        "\n1. Search for relevant papers using the search_papers_tool"
        "\n2. Format the results with both paper details and citations"
        "\n3. If the query mentions citations, include them automatically"
        "\n4. If the query asks for summaries, include paper summaries"
        "\n5. If asked about recent papers, filter by date"
        "\nKeep responses focused and structured."
    ),
)

@research_agent.tool_plain
def summarize_paper(paper: Paper) -> str:
    """Generate a brief summary based on paper's abstract."""
    try:
        if paper.abstract:
            # Return first 2 sentences or 200 characters
            summary = paper.abstract.split('. ')[:2]
            return f"Summary: {'. '.join(summary)}."
        return f"Summary: This paper focuses on {paper.title}."
    except Exception as e:
        logger.error(f"Error in summarize_paper: {e}")
        return f"Summary could not be generated."

@research_agent.tool
async def search_papers_tool(ctx: RunContext, query: str, max_results: int = 5) -> str:
    try:
        logger.info(f"Agent is searching arXiv for query: {query}")
        papers = search_arxiv(query, max_results)
        if not papers:
            return "No papers found for your query."

        formatted_response = ["### Found Papers:\n"]
        
        for idx, paper in enumerate(papers, 1):
            paper_details = [
                f"{idx}. **Title:** {paper.title}",
                f"   **Authors:** {', '.join(paper.authors)}",
                f"   **Published:** {paper.published_date}",
                f"   **URL:** [{paper.url}]({paper.url})"
            ]
            
            if "summary" in query.lower() or "summarize" in query.lower():
                summary = summarize_paper(paper)
                paper_details.append(f"   **Summary:** {summary}")
            
            formatted_response.append("\n".join(paper_details) + "\n")

        return "\n".join(formatted_response)

    except Exception as e:
        logger.error(f"Error in search_papers_tool: {e}", exc_info=True)
        return f"Error occurred while searching for papers: {str(e)}"
@research_agent.tool_plain
def get_paper_count(papers: List[Paper]) -> str:
    """Get the count of papers found."""
    return f"Found {len(papers)} papers matching your query."

@research_agent.tool_plain
def format_citation(paper: Paper) -> str:
    """Format a paper citation in APA style."""
    authors = ", ".join(paper.authors)
    return f"{authors}. {paper.title}. arXiv preprint {paper.url}"

def is_single_keyword(query: str) -> bool:
    """Determines if the query is a single keyword."""
    query = query.strip()
    return bool(re.fullmatch(r'\b\w+\b', query))