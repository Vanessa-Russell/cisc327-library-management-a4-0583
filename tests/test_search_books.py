import pytest
import services.library_service as library_service
from services.library_service import search_books_in_catalog

def test_search_by_title_partial_match():
    """Search books by partial title, case-insensitive."""
    results = search_books_in_catalog("great gatsby", "title")
    assert isinstance(results, list)
    for book in results:
        assert "title" in book
        assert "great gatsby" in book["title"].lower()

def test_search_by_author_partial_match():
    """Search books by partial author name, case-insensitive."""
    results = search_books_in_catalog("fitzgerald", "author")
    assert isinstance(results, list)
    for book in results:
        assert "author" in book
        assert "fitzgerald" in book["author"].lower()

def test_search_by_isbn_exact_match():
    """Search books by exact ISBN."""
    isbn = "9780743273565"  # Correct ISBN for The Great Gatsby
    results = search_books_in_catalog(isbn, "isbn")
    assert isinstance(results, list)
    for book in results:
        assert "isbn" in book
        assert book["isbn"] == isbn

def test_search_no_results():
    """Search with term that matches no book."""
    results = search_books_in_catalog("nonexistentsearchterm", "title")
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_empty_term():
    """Search with empty term returns empty list or error."""
    results = search_books_in_catalog("", "title")
    assert isinstance(results, list)
    assert len(results) == 0

def test_search_invalid_type_returns_empty_list():
    assert search_books_in_catalog("anything", "publisher") == []

def test_search_books_invalid_search_type_returns_empty():
    """If search_type is not title/author/isbn, function should return an empty list."""
    results = library_service.search_books_in_catalog("Anything", "publisher")
    assert results == []

def test_search_books_non_string_arguments_returns_empty():
    """Non-string search_term/search_type should safely return an empty list."""
    results = library_service.search_books_in_catalog(123, 456)  # type: ignore[arg-type]
    assert results == []
