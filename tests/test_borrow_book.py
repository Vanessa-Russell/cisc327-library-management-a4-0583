import pytest
import database
import services.library_service as library_service
from services.library_service import (
    borrow_book_by_patron
    )

def test_borrow_book_missing_patron_id():
    """Test borrowing a book with missing patron ID."""
    success, message = borrow_book_by_patron("", 1)  # Empty patron ID
    assert success == False
    assert "invalid patron id" in message.lower() or "missing patron id" in message.lower()

def test_borrow_book_invalid_patron_id():
    """Test borrowing a book with invalid patron ID format."""
    success, message = borrow_book_by_patron("abc123", 1)
    assert success == False
    assert "invalid patron id" in message.lower()

def test_borrow_book_book_not_found():
    """Test borrowing a book that does not exist."""
    success, message = borrow_book_by_patron("123456", 99999)
    assert success == False
    assert "book not found" in message.lower()

def test_borrow_book_negative_book_id():
    """Test borrowing with negative book_id."""
    success, message = borrow_book_by_patron("123456", -1)
    # Most likely book not found
    assert success == False
    assert "book not found" in message.lower()