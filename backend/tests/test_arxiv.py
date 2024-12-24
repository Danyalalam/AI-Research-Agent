import arxiv

def test_arxiv_search():
    client = arxiv.Client()
    search = arxiv.Search(
        query="machine learning",
        max_results=5,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    for result in client.results(search):
        paper = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "url": result.entry_id
        }
        results.append(paper)
    
    assert len(results) > 0
    for paper in results:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"URL: {paper['url']}\n")

if __name__ == "__main__":
    test_arxiv_search()