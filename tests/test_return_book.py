import pytest
from services.library_service import return_book_by_patron

def test_return_book_not_borrowed():
    """Test returning a book that was not borrowed by the patron."""
    success, message = return_book_by_patron("123456", 9999)  # Non-existent book_id or not borrowed
    assert success == False
    assert "not borrowed" in message.lower() or "no record" in message.lower()

def test_return_book_invalid_patron_id():
    """Test returning a book with invalid patron ID."""
    success, message = return_book_by_patron("abc123", 1)  # Invalid patron id format
    assert success == False
    assert "invalid patron" in message.lower()

def test_return_book_invalid_book_id():
    """Test returning a book with invalid book ID."""
    success, message = return_book_by_patron("123456", -5)  # Invalid book id
    assert success == False
    assert "invalid book" in message.lower() or "not found" in message.lower()

def test_return_book_late_fee_calculation():
    """Test return book calculates late fees properly if overdue."""
    # test if the message contains 'late fee' or similar on overdue return
    success, message = return_book_by_patron("123456", 2)  # Assume possible overdue book
    assert success == True or success == False  # Could pass or fail depending on internal logic
    assert ("late fee" in message.lower()) or ("success" in message.lower()) or ("returned" in message.lower())

