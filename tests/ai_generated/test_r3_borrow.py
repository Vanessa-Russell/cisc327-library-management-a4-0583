# Tests for R3: Book Borrowing Interface. These cover successful borrowing and failures
# due to availability, book/patron ID issues, and the 6-digit patron format rule.

from services import library_service
import database

def test_r3_borrow_failure_not_available():
    """Negative case: Attempt to borrow a book with zero available copies."""
    isbn = "9783000000002"
    library_service.add_book_to_catalog("Sold Out Book", "S. O. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    patron_id_a = "234567"
    patron_id_b = "345678"
    
    library_service.borrow_book_by_patron(patron_id_a, book_id) # Borrows the only copy
    
    success, message = library_service.borrow_book_by_patron(patron_id_b, book_id)
    assert success is False
    assert "not available" in message.lower()

def test_r3_borrow_failure_invalid_patron_id_format():
    """Negative case: Attempt to borrow with a non 6-digit patron ID."""
    isbn = "9783000000003"
    library_service.add_book_to_catalog("Valid Book", "V. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    invalid_patron_id = "12345" # 5 digits
    
    success, message = library_service.borrow_book_by_patron(invalid_patron_id, book_id)
    assert success is False
    assert "invalid patron id" in message.lower()
    
def test_r3_borrow_failure_book_not_found():
    """Negative case: Attempt to borrow a book with a non-existent book_id."""
    patron_id = "456789"
    non_existent_book_id = 99999
    
    success, message = library_service.borrow_book_by_patron(patron_id, non_existent_book_id)
    assert success is False
    assert "book not found" in message.lower()

    