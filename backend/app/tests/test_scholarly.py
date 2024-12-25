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

def test_scholarly_search():
    search_query = "machine learning"
    search_results = scholarly.search_pubs(search_query)

    results = []
    for _ in range(5):
        try:
            pub = next(search_results)
            bib = pub.get('bib', {})

            # Construct URL using available identifiers
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

    assert len(results) > 0, "No papers found for the query."
    for paper in results:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"URL: {paper['url']}\n")

if __name__ == "__main__":
    test_scholarly_search()