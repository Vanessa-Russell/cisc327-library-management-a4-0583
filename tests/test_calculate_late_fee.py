import pytest
import services.library_service as library_service
from services.library_service import calculate_late_fee_for_book

def test_late_fee_returns_dict():
    """Test that the function returns a dict."""
    result = calculate_late_fee_for_book("any_id", 1)
    assert isinstance(result, dict)

def test_late_fee_contains_expected_keys():
    """Check that returned dict has keys 'fee_amount', 'days_overdue', 'status'."""
    result = calculate_late_fee_for_book("any_id", 1)
    for key in ["fee_amount", "days_overdue", "status"]:
        assert key in result

def test_late_fee_non_negative_fee_and_days():
    """Late fee and days overdue should be non-negative numbers."""
    result = calculate_late_fee_for_book("any_id", 1)
    assert isinstance(result.get("fee_amount"), (int, float))
    assert result["fee_amount"] >= 0
    assert isinstance(result.get("days_overdue"), int)
    assert result["days_overdue"] >= 0


def test_late_fee_handles_invalid_patron_or_book():
    """Invalid inputs return an error status and zero fee due to format validation failure."""
    result_patron_fail = calculate_late_fee_for_book("invalid_patron", 1) # Use valid book ID placeholder
    assert isinstance(result_patron_fail, dict)
    assert result_patron_fail.get("status") == "Invalid patron ID"
    assert result_patron_fail.get("fee_amount") == 0.0
    result_book_fail = calculate_late_fee_for_book("123456", -999) # Use valid patron ID placeholder
    assert isinstance(result_book_fail, dict)
    assert result_book_fail.get("status") == "Invalid book ID"
    assert result_book_fail.get("fee_amount") == 0.0

def test_calculate_late_fee_book_not_found_returns_zero_fee():
    """If the book_id does not exist, status is 'Book not found' and fee is zero."""
    patron_id = "123456"
    # Pick a very large book_id that won't exist
    missing_book_id = 999999
    report = library_service.calculate_late_fee_for_book(patron_id, missing_book_id)
    assert report["status"] == "Book not found"
    assert report["fee_amount"] == 0.0
    assert report["days_overdue"] == 0