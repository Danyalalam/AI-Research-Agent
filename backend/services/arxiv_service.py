import arxiv

def search_arxiv(query: str, max_results: int = 5):
    """
    Searches ArXiv for papers matching the query.

    :param query: The search query string.
    :param max_results: Maximum number of results to retrieve.
    :return: List of dictionaries containing paper details.
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = []
    for result in search.results():
        paper = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "url": result.entry_id  # Direct URL to the paper on ArXiv
        }
        results.append(paper)
    
    return results