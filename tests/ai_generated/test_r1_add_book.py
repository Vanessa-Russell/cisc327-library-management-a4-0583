# Tests for R1: Add Book To Catalog. These cases verify successful addition and ensure
# strict failure for duplicate ISBNs and invalid inputs, checking the (bool, str) return.

from services import library_service
import database

def test_r1_add_book_duplicate_isbn_fails():
    """Negative case: Attempt to add a book with an existing ISBN must fail and not merge."""
    isbn = "9781000000002"
    # First addition (success)
    library_service.add_book_to_catalog("First Edition", "A. Author", isbn, 1)
    
    # Second addition (failure)
    success, message = library_service.add_book_to_catalog("Second Edition", "A. Author", isbn, 1)
    assert success is False
    assert "isbn" in message.lower()
    assert "exists" in message.lower()
    
def test_r1_add_book_invalid_isbn_format():
    """Negative case: Attempt to add a book with an invalid, short ISBN."""
    isbn = "12345"
    success, message = library_service.add_book_to_catalog("Bad ISBN Book", "B. Author", isbn, 1)
    assert success is False
    assert "isbn" in message.lower()
    
def test_r1_add_book_invalid_copies():
    """Negative case: Attempt to add a book with zero total copies."""
    isbn = "9781000000004"
    success, message = library_service.add_book_to_catalog("Zero Stock", "Z. Author", isbn, 0)
    assert success is False
    assert "copies" in message.lower()





    