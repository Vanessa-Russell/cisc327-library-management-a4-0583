# Tests for R2: Book Catalog Display. These tests use search_books_in_catalog as the
# display proxy, verifying the structure and content of returned book records.

from services import library_service
import database

def test_r2_catalog_display_after_addition():
    """Positive case: Verify a book added to the catalog is retrievable via search."""
    isbn = "9782000000001"
    library_service.add_book_to_catalog("Test Catalog Title", "C. Author", isbn, 5)
    
    results = library_service.search_books_in_catalog("Test Catalog Title", "title")
    assert len(results) == 1
    book = results[0]
    assert book['isbn'] == isbn
    assert book['total_copies'] == 5
    assert book['available_copies'] == 5

def test_r2_catalog_display_no_matches_found():
    """Negative case: Searching for a non-existent title should return an empty list."""
    isbn = "9782000000003"
    library_service.add_book_to_catalog("Lonely Book", "L. Author", isbn, 1)
    
    results = library_service.search_books_in_catalog("NonExistentBook", "title")
    assert results == []

def test_r2_catalog_display_invalid_search_type():
    """Negative case: Using an unsupported search type returns an empty list (no error string)."""
    isbn = "9782000000004"
    library_service.add_book_to_catalog("Valid Book", "V. Author", isbn, 1)
    
    results = library_service.search_books_in_catalog("Valid Book", "genre")
    assert results == []






    