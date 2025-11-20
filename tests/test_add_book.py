import pytest
from services.library_service import (
    add_book_to_catalog
)

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_missing_title():
    """Test adding a book with missing title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    assert success == False
    assert "title is required" in message.lower()

def test_add_book_title_too_long():
    """Test adding a book with title exceeding 200 characters."""
    long_title = "T" * 201
    success, message = add_book_to_catalog(long_title, "Test Author", "1234567890123", 5)
    assert success == False
    assert "less than 200 characters" in message.lower()

def test_add_book_missing_author():
    """Test adding a book with missing author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    assert success == False
    assert "author is required" in message.lower()

def test_add_book_author_too_long():
    """Test adding a book with author exceeding 100 characters."""
    long_author = "A" * 101
    success, message = add_book_to_catalog("Test Book", long_author, "1234567890123", 5)
    assert success == False
    assert "less than 100 characters" in message.lower()

def test_add_book_invalid_total_copies_zero():
    """Test adding a book with zero copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    assert success == False
    assert "positive integer" in message.lower()

def test_add_book_invalid_total_copies_negative():
    """Test adding a book with negative copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -5)
    assert success == False
    assert "positive integer" in message.lower()
