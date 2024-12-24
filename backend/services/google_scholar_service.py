from scholarly import scholarly

def construct_url(bib):
    """
    Constructs a URL for the publication using available identifiers.

    Priority:
    1. DOI
    2. arXiv ID (eprint)
    3. Publication URL (if available)
    4. Fallback to 'No URL available.'
    """
    doi = bib.get('doi')
    eprint = bib.get('eprint')
    url = bib.get('pub_url') or bib.get('url')

    if doi:
        return f"https://doi.org/{doi}"
    elif eprint:
        return f"https://arxiv.org/abs/{eprint}"
    elif url:
        return url
    else:
        return 'No URL available.'

def search_google_scholar(query: str, max_results: int = 5):
    """
    Searches Google Scholar for papers matching the query.

    :param query: The search query string.
    :param max_results: Maximum number of results to retrieve.
    :return: List of dictionaries containing paper details.
    """
    search_results = scholarly.search_pubs(query)
    results = []
    
    for _ in range(max_results):
        try:
            pub = next(search_results)
            bib = pub.get('bib', {})
            url = construct_url(bib)
            
            paper = {
                "title": bib.get('title', 'No title available.'),
                "authors": bib.get('author', []),
                "abstract": bib.get('abstract', 'No abstract available.'),
                "url": url
            }
            results.append(paper)
        except StopIteration:
            break
        except KeyError as e:
            print(f"Missing key in publication: {e}")
    
    return results