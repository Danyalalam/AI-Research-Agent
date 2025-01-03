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
        "\n2. For citation requests, use format_citation_tool and don't ask for more context just generate on the basis of what is available"
        "\n3. For summary requests, use summarize_paper_tool and don't ask for more context just generate on the basis of what is available."
        "\n4. Always include paper URLs and full details"
        "\nMaintain academic formatting and clarity."
    ),
)

@research_agent.tool
async def summarize_paper_tool(ctx: RunContext, paper: Paper) -> str:
    """
    Generate AI-powered analysis of paper content from abstract.
    
    Input:
        paper: Paper object containing title, authors, abstract
    
    Output:
        Markdown formatted summary with sections:
        - Research Focus
        - Key Methods
        - Main Findings
        - Potential Impact
    
    Example output:
        **Research Focus:** Quantum Computing
        **Key Points:** Novel quantum algorithm...
        **Impact:** Advances in quantum theory...
    """
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
async def search_papers_tool(ctx: RunContext, query: str, max_results: int = 5, citation_style: str = "APA", include_summary: bool = False) -> str:
    try:
        papers = search_arxiv(query, max_results)
        if not papers:
            return "No papers found for your query."

        formatted_response = ["### Found Papers:\n"]
        
        for idx, paper in enumerate(papers, 1):
            paper_details = [
                f"{idx}. **Title:** [{paper.title}]({paper.url})",
                f"   **Authors:** {', '.join(paper.authors)}",
                f"   **Published:** {paper.published_date}"
            ]
            
            if include_summary:
                summary = await summarize_paper_tool(ctx, paper)
                paper_details.append(f"\n   {summary}")
                
            if include_summary or "citation" in query.lower() or "cite" in query.lower():
                citation = await format_citation_tool(ctx, paper, citation_style)
                paper_details.append(f"\n   {citation}")
            
            formatted_response.append("\n".join(paper_details) + "\n")

        return "\n".join(formatted_response)

    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Error occurred while searching for papers: {str(e)}"

@research_agent.tool
async def format_citation_tool(ctx: RunContext, paper: Paper, style: str = "APA") -> str:
    """
    Generates formatted citations for academic papers in multiple styles.
    
    Input:
        paper: Paper object with title, authors, URL, and date
        style: Citation style (e.g., APA, MLA, Chicago)
    
    Output:
        Formatted citation with clickable URL
    """
    try:
        # Define citation formats
        citation_formats = {
            "APA": lambda p: f"{', '.join(p.authors)} ({p.published_date[:4]}). {p.title}. arXiv: [{p.url}]({p.url})",
            "MLA": lambda p: f"{', '.join(p.authors)}. \"{p.title}.\" arXiv, {p.published_date[:4]}, {p.url}.",
            "Chicago": lambda p: f"{', '.join(p.authors)}. {p.published_date[:4]}. \"{p.title}.\" arXiv. {p.url}.",
        }

        # Get the formatter based on requested style
        formatter = citation_formats.get(style.upper())

        if not formatter:
            return f"Unsupported citation style: {style}. Supported styles are APA, MLA, Chicago."

        citation = formatter(paper)
        
        return f"**Citation ({style.upper()} Format):**\n{citation}"
    
    except Exception as e:
        logger.error(f"Citation generation failed: {e}")
        return f"Could not generate {style.upper()} citation for: {paper.title}"