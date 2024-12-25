import arxiv
from typing import List
from pydantic import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Paper(BaseModel):
    title: str
    authors: List[str]
    url: str
    abstract: str
    published_date: str

def search_arxiv(query: str, max_results: int = 5) -> List[Paper]:
    """
    Search for research papers on arXiv based on the query.
    Returns list of Paper objects with titles, authors, URLs, abstracts and dates.
    """
    try:
        logger.info(f"Searching arXiv for: {query}")
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            date_str = result.published.strftime("%Y-%m-%d") if result.published else "No date"

            # Get PDF URL from arxiv entry
            pdf_url = result.pdf_url if hasattr(result, 'pdf_url') else None
            # Fall back to entry ID (abstract page) if PDF URL not available
            url = pdf_url if pdf_url else f"https://arxiv.org/abs/{result.entry_id.split('/')[-1]}"
            
            paper = Paper(
                title=result.title,
                authors=[author.name for author in result.authors],
                url=url,
                abstract=result.summary,
                published_date=date_str
            )
            papers.append(paper)
            logger.info(f"Found paper: {paper.title} with URL: {paper.url}")
            
        return papers
    except Exception as e:
        logger.error(f"Error searching arXiv: {e}", exc_info=True)
        return []