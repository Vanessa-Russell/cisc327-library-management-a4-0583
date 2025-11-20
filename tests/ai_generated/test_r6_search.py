# Tests for R6: Book Search Functionality. These cases verify all valid search types
# (title, author, ISBN) and ensure that invalid queries return an empty list.

from services import library_service
import database

def test_r6_search_by_author_multiple_matches():
    """Positive case: Search for an author who has multiple books in the catalog."""
    isbn1 = "9786000000002"
    isbn2 = "9786000000003"
    library_service.add_book_to_catalog("Book Alpha", "Z. Smith", isbn1, 1)
    library_service.add_book_to_catalog("Book Beta", "Z. Smith", isbn2, 1)
    
    results = library_service.search_books_in_catalog("Z. Smith", "author")
    assert len(results) == 2
    titles = {b['title'] for b in results}
    assert "Book Alpha" in titles
    assert "Book Beta" in titles

def test_r6_search_by_isbn_exact_match():
    """Positive case: Search for a book using its exact ISBN."""
    isbn = "9786000000004"
    library_service.add_book_to_catalog("ISBN Looker", "I. Author", isbn, 1)
    
    results = library_service.search_books_in_catalog(isbn, "isbn")
    assert len(results) == 1
    assert results[0]['isbn'] == isbn

def test_r6_search_no_match():
    """Negative case: Search for a term that does not match any book."""
    isbn = "9786000000005"
    library_service.add_book_to_catalog("Exist Book", "E. Author", isbn, 1)
    
    results = library_service.search_books_in_catalog("NonExistentTerm", "title")
    assert results == []

def test_r6_search_invalid_type_returns_empty_list():
    """Negative case: Search using an unsupported search type returns an empty list."""
    isbn = "9786000000006"
    library_service.add_book_to_catalog("Book", "Author", isbn, 1)
    
    results = library_service.search_books_in_catalog("Book", "genre")
    assert results == []


    