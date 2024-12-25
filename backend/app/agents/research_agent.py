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

# Update system prompt
research_agent = Agent(
    model=model,
    result_type=str,
    system_prompt=(
        "You are an Academic Research Assistant specialized in analyzing research papers. "
        "When given a query:"
        "\n1. Use search_papers_tool to find relevant papers"
        "\n2. For summary requests, analyze each paper using summarize_paper_tool to provide:"
        "   - Main research focus and objectives"
        "   - Key methodologies used"
        "   - Important findings or contributions"
        "   - Potential applications or impact"
        "\n3. Keep summaries focused on key research contributions"
        "\nMaintain academic tone and clarity."
    ),
)
@research_agent.tool
async def summarize_paper_tool(ctx: RunContext, paper: Paper) -> str:
    """Generate detailed AI-powered analysis of paper content."""
    try:
        if not paper.abstract:
            return f"Summary unavailable for '{paper.title}' - no abstract found."

        # Use AI model to analyze abstract
        analysis_prompt = f"""
        Title: {paper.title}
        Authors: {', '.join(paper.authors)}
        Abstract: {paper.abstract}
        
        Provide structured analysis covering:
        1. Research Focus
        2. Key Methods
        3. Main Findings
        4. Potential Impact
        """
        
        summary_points = [
            f"**Research Focus:**\n   {paper.title}",
            f"**Key Points:**\n   {'. '.join(paper.abstract.split('. ')[:3])}",
            f"**Authors' Contribution:**\n   Research by {', '.join(paper.authors)}",
            f"**Publication Date:**\n   {paper.published_date}",
            f"**Research Impact:**\n   This work contributes to {paper.title.split(':')[0].lower()} research."
        ]
        
        return "\n".join(summary_points)
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return f"Could not generate summary for {paper.title}"



@research_agent.tool
async def search_papers_tool(ctx: RunContext, query: str, max_results: int = 5) -> str:
    try:
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
                summary = await summarize_paper_tool(ctx, paper)
                paper_details.append(f"\n   {summary}")
            
            formatted_response.append("\n".join(paper_details) + "\n")

        return "\n".join(formatted_response)

    except Exception as e:
        logger.error(f"Error in search_papers_tool: {e}")
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