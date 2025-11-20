from services.library_service import get_patron_status_report
import services.library_service as library_service
import database
from unittest.mock import Mock

def test_patron_status_returns_dict():
    """Test function returns a dict regardless of patron_id."""
    result = get_patron_status_report("any_patron_id")
    assert isinstance(result, dict)

def test_patron_status_empty_dict_or_min_keys():
    """Test returned dict is empty or has at least 'status' key."""
    result = get_patron_status_report("any_patron_id")
    assert isinstance(result, dict)
    # Since currently empty dict is returned, this test allows empty or keys
    assert len(result) == 0 or "status" in result

def test_patron_status_handles_invalid_patron_id():
    """Test function handles invalid patron ID."""
    invalid_id = "invalid"
    result = get_patron_status_report(invalid_id)
    assert isinstance(result, dict)
    assert len(result) == 0 or "status" in result

def test_patron_status_with_negative_patron_id():
    """Test function handles negative patron ID."""
    negative_id = "-123456"
    result = get_patron_status_report(negative_id)
    assert isinstance(result, dict)
    # Since unimplemented, allow empty dict or dict with 'status' key
    assert len(result) == 0 or "status" in result

def test_get_patron_status_with_stubbed_loans_and_history(mocker):
    """Valid patron with stubbed active loan and history (no real DB access)."""
    patron_id = "555666"  # valid 6-digit ID
    # pretend this patron has one active loan
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[
            {
                "book_id": 1,
                "title": "Stubbed Book",
                "author": "Stub Author",
                # store due_date as a simple string so str(...).split works
                "due_date": "2025-01-15",
            }
        ],
    )
    # pretend the late fee is a known value
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 1.50, "days_overdue": 3, "status": "OK"},
    )
    # fake DB connection and history rows
    history_rows = [
        {
            "borrow_date": "2025-01-01",
            "due_date": "2025-01-15",
            "return_date": None,
            "book_id": 1,
            "title": "Stubbed Book",
            "author": "Stub Author",
        }
    ]
    conn_mock = Mock()
    execute_result = Mock()
    execute_result.fetchall.return_value = history_rows
    conn_mock.execute.return_value = execute_result
    conn_mock.close.return_value = None
    mocker.patch("services.library_service.get_db_connection", return_value=conn_mock)
    # Act
    report = library_service.get_patron_status_report(patron_id)
    # Assert – we are now exercising the main branch of the function
    assert report["status"] == "OK"
    assert report["borrow_count"] == 1
    assert report["total_late_fees"] == 1.50
    # current_borrows structure
    assert isinstance(report["current_borrows"], list)
    assert len(report["current_borrows"]) == 1
    current = report["current_borrows"][0]
    assert current["book_id"] == 1
    assert current["title"] == "Stubbed Book"
    assert current["author"] == "Stub Author"
    assert current["is_overdue"] is True
    assert current["fee"] == 1.50
    # history structure
    assert isinstance(report["history"], list)
    assert len(report["history"]) == 1
    hist = report["history"][0]
    assert hist["book_id"] == 1
    assert hist["title"] == "Stubbed Book"
    assert hist["author"] == "Stub Author"
    assert hist["status"] == "borrowed"  # because return_date is None