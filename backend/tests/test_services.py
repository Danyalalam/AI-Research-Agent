import pytest
from app.services.arxiv_service import search_arxiv
from app.services.google_scholar_service import search_google_scholar

@pytest.fixture
def sample_query():
    return "machine learning"

def test_search_arxiv(sample_query):
    results = search_arxiv(sample_query, max_results=3)
    assert len(results) == 3
    for paper in results:
        assert "title" in paper
        assert "authors" in paper
        assert "abstract" in paper
        assert "url" in paper

def test_search_google_scholar(sample_query):
    results = search_google_scholar(sample_query, max_results=3)
    assert len(results) == 3
    for paper in results:
        assert "title" in paper
        assert "authors" in paper
        assert "abstract" in paper
        assert "url" in paper