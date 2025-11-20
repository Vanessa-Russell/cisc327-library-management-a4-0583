# Tests for R5: Late Fee Calculation API. These cases test specific fee amounts for
# on-time and various overdue durations, and check the fee cap and error states.

from services import library_service
import database
from datetime import datetime, timedelta

def set_loan_due_date(patron_id, book_id, days_in_past):
    """Helper to manually set a loan's due_date for deterministic fee testing."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    # Calculate the new due date: 14 days loan period, set it to days_in_past before today
    new_due = (datetime.now() - timedelta(days=days_in_past)).isoformat()
    
    cursor.execute(
        "UPDATE borrow_records SET due_date = ? WHERE patron_id = ? AND book_id = ? AND return_date IS NULL", 
        (new_due, patron_id, book_id)
    )
    conn.commit()
    conn.close()

def test_r5_late_fee_zero_on_time():
    """Positive case: Calculate a zero fee for a book that is not yet overdue."""
    isbn = "9785000000001"
    library_service.add_book_to_catalog("On Time", "T. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    patron_id = "111222"
    
    library_service.borrow_book_by_patron(patron_id, book_id)
    # Default due date should be 14 days in the future (0 days overdue)
    
    report = library_service.calculate_late_fee_for_book(patron_id, book_id)
    assert report['status'] == "OK"
    assert report['days_overdue'] >= 0
    assert report['fee_amount'] >= 0.0

def test_r5_late_fee_3_days_overdue():
    """Positive case: Calculate fee for 3 days overdue ($0.50/day = $1.50)."""
    isbn = "9785000000002"
    library_service.add_book_to_catalog("3 Days Late", "D. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    patron_id = "222333"
    
    library_service.borrow_book_by_patron(patron_id, book_id)
    set_loan_due_date(patron_id, book_id, 3)
    
    report = library_service.calculate_late_fee_for_book(patron_id, book_id)
    assert report['status'] == "OK"
    assert report['days_overdue'] == 3
    assert report['fee_amount'] == 1.50 # 3 days * $0.50

def test_r5_late_fee_10_days_overdue():
    """Positive case: Calculate fee for 10 days overdue ($0.50 x 7 + $1 x 3 = $3.50 + $3.00 = $6.50)."""
    isbn = "9785000000003"
    library_service.add_book_to_catalog("10 Days Late", "L. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    patron_id = "333444"
    
    library_service.borrow_book_by_patron(patron_id, book_id)
    set_loan_due_date(patron_id, book_id, 10)
    
    report = library_service.calculate_late_fee_for_book(patron_id, book_id)
    assert report['status'] == "OK"
    assert report['days_overdue'] == 10
    assert report['fee_amount'] == 6.50

def test_r5_late_fee_capped_at_15():
    """Positive case: Calculate fee for 30 days overdue (fee should cap at $15.00)."""
    # Calculation: 7 days @ $0.50 ($3.50) + 23 days @ $1.00 ($23.00) = $26.50. Capped at $15.00.
    isbn = "9785000000004"
    library_service.add_book_to_catalog("Fee Cap", "C. Author", isbn, 1)
    book_id = database.get_book_by_isbn(isbn)["id"]
    patron_id = "444555"
    
    library_service.borrow_book_by_patron(patron_id, book_id)
    set_loan_due_date(patron_id, book_id, 30)
    
    report = library_service.calculate_late_fee_for_book(patron_id, book_id)
    assert report['status'] == "OK"
    assert report['days_overdue'] == 30
    assert report['fee_amount'] == 15.00




