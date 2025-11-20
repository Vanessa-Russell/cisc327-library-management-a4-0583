"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System,
interacting with the database module to manage book, patron, and loan data.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from ..database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, 
    get_patron_borrowed_books, get_db_connection
)

# Define constants for clarity
LOAN_PERIOD_DAYS = 14
MAX_LOAN_LIMIT = 5
FEE_RATE_1 = 0.50 # $0.50/day for first 7 days overdue
FEE_RATE_2 = 1.00  # $1.00/day after 7 days overdue
MAX_FEE = 15.00 # Maximum late fee limit

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    # Adds a new book record to the catalog with specified copies.
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    # Check for duplicate ISBN (Duplicate ISBN fails)
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, f"A book with ISBN {isbn} already exists."
    # Insert new book (available copies = total copies initially)
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    #Records a book loan for a patron, checking availability and limits.
    # Validate patron ID (6-digit check) 
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    # Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    # Check availability
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    # Check patron's borrowing limit (Max 5 books)
    current_borrowed = get_patron_borrow_count(patron_id)
    if current_borrowed >= MAX_LOAN_LIMIT:
        return False, f"You have reached the maximum borrowing limit of {MAX_LOAN_LIMIT} books."
    # Calculate due date
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=LOAN_PERIOD_DAYS)
    # Insert borrow record
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    # Update book availability (-1)
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    #Processes the return of a book by a patron.
    # Validate inputs
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID: must be 6 digits."
    if not isinstance(book_id, int) or book_id <= 0:
        return False, "Invalid book ID."
    # Check if the book exists to provide a specific error if possible
    book = get_book_by_id(book_id)
    if not book:
        # Returning a failure message consistent with the test failure
        return False, "Invalid book: no record found." 
    # Calculate late fee
    fee_report = calculate_late_fee_for_book(patron_id, book_id)
    # Mark the borrow as returned. 
    returned_count = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if returned_count == 0:
        return False, "No record found: this book was not borrowed by the patron."
    fee_amount = fee_report['fee_amount']
    current_avail = int(book.get("available_copies", 0))
    total_copies = int(book.get("total_copies", 0))
    # Prevent availability from exceeding total copies
    if current_avail < total_copies:
        update_book_availability(book_id, +1)
    fee_msg = f" Late fee: ${fee_amount:.2f}." if fee_amount > 0 else " No late fee."
    return True, f"Book returned successfully.{fee_msg}"

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    # Calculates the late fee based on the due date of the active loan.
    # Input validation
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid patron ID'}
    if not isinstance(book_id, int) or book_id <= 0:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid book ID'}
    # Ensure book exists
    book = get_book_by_id(book_id)
    if not book:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Book not found'}
    # Retrieve the patron's active borrow record for this specific book
    try:
        active_loans = get_patron_borrowed_books(patron_id)
        # Find the specific active record for the book_id
        rec = next((r for r in active_loans if int(r.get('book_id')) == int(book_id)), None)
    except Exception:
        rec = None
    if not rec:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No active borrow for this patron/book'}
    # Compute overdue days
    due_date = rec['due_date']
    today = datetime.now()
    # Calculate difference
    days_overdue = max(0, (today.date() - due_date.date()).days)
    # Tiered fee calculation: $0.50/day for 1st 7 days, $1/day after, max $15
    fee = 0.0
    if days_overdue > 0:
        # Apply the $0.50 rate for the first 7 days overdue
        first7 = min(days_overdue, 7)
        # Apply the $1.00 rate for the remaining days
        rest = max(days_overdue - 7, 0)
        fee = (FEE_RATE_1 * first7) + (FEE_RATE_2 * rest)
        # Apply maximum cap
        fee = min(fee, MAX_FEE)
    return {
        'fee_amount': round(fee, 2),
        'days_overdue': int(days_overdue),
        'status': 'OK'
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    # Searches the book catalog by title, author, or ISBN.
    # Input checks and normalization
    if not isinstance(search_term, str) or not isinstance(search_type, str):
        return []
    q = search_term.strip()
    st = search_type.strip().lower()
    if not q or st not in {"title", "author", "isbn"}:
        return [] # Invalid type or empty term returns []
    # Optimized search for exact ISBN
    if st == "isbn":
        book = get_book_by_isbn(q)
        return [book] if book else []
    # Full catalog search for title/author
    all_books = get_all_books()
    needle = q.lower()
    results: List[Dict] = []
    for b in all_books:
        # Retrieve the value based on the search type
        val = (b.get(st) or "")
        if isinstance(val, str) and needle in val.lower():
            results.append(b)     
    return results

def get_patron_status_report(patron_id: str) -> Dict:
    # Generates a full status report for a patron, including active loans, fees, and history.
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {"status": "Invalid patron ID"}
    # Process Active Loans and Calculate Total Fees
    active_loans = get_patron_borrowed_books(patron_id) 
    current_borrows: List[Dict] = []
    total_fees = 0.0
    for rec in active_loans:
        fee_info = calculate_late_fee_for_book(patron_id, int(rec["book_id"]))
        fee_amt = float(fee_info.get("fee_amount", 0.0))
        total_fees += fee_amt   
        # Format due date nicely
        due_date_str = rec["due_date"].strftime("%Y-%m-%d") if hasattr(rec["due_date"], "strftime") else str(rec["due_date"]).split(" ")[0]   
        current_borrows.append({
            "book_id": rec["book_id"],
            "title": rec["title"],
            "author": rec["author"],
            "due_date": due_date_str,
            "is_overdue": fee_info['days_overdue'] > 0, 
            "fee": round(fee_amt, 2),
        })
    # Full Borrowing History
    conn = get_db_connection()
    # Query all borrow records for the patron
    rows = conn.execute(
        """
        SELECT br.patron_id, br.book_id, br.borrow_date, br.due_date, br.return_date,
               b.title, b.author
        FROM borrow_records br
        JOIN books b ON b.id = br.book_id
        WHERE br.patron_id = ?
        ORDER BY datetime(br.borrow_date) DESC, br.id DESC
        """,
        (patron_id,)
    ).fetchall()
    conn.close()
    history: List[Dict] = []
    for r in rows:
        bd = str(r["borrow_date"]).split("T")[0] if r["borrow_date"] else None
        dd = str(r["due_date"]).split("T")[0] if r["due_date"] else None
        rd = str(r["return_date"]).split("T")[0] if r["return_date"] else None
        history.append({
            "book_id": r["book_id"],
            "title": r["title"],
            "author": r["author"],
            "borrow_date": bd,
            "due_date": dd,
            "return_date": rd,
            "status": "returned" if r["return_date"] else "borrowed",
        })
    # Final Report Structure
    return {
        "current_borrows": current_borrows,
        "total_late_fees": round(total_fees, 2),
        "borrow_count": len(active_loans), # R7 requires this to be the count of CURRENT loans
        "history": history,
        "status": "OK",
    }

def pay_late_fees(patron_id: str, book_id: int, payment_gateway) -> Dict[str, Any]:
    # validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            "success": False,
            "status": "Invalid patron ID",
            "transaction_id": None,
            "amount_charged": 0.0,
        }
    # validate book ID
    if not isinstance(book_id, int) or book_id <= 0:
        return {
            "success": False,
            "status": "Invalid book ID",
            "transaction_id": None,
            "amount_charged": 0.0,
        }
    # make sure book exists
    book = get_book_by_id(book_id)
    if not book:
        return{
            "success": False,
            "status": "Book not found",
            "transaction_id": None,
            "amount_charged": 0.0,
        }
    # calculate late fee
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    amount = float(fee_info.get("fee_amount", 0.0))
    # if no fees are due do not call payment gateway
    if amount <= 0:
        return {
            "success": True,
            "status": "No late fees due",
            "transaction_id": None,
            "amount_charged": 0.0,
        }
    # call external payment gateway
    try:
        result = payment_gateway.process_payment(patron_id, amount)
    except Exception as exc:
        return {
            "success": False,
            "status": f"Payment error: {exc}",
            "transaction_id": None,
            "amount_charged": 0.0,
        }
    # normalize result
    if isinstance(result, dict):
        success = bool(result.get("success"))
        tx_id = result.get("transaction_id")
        status_msg = result.get("message", "OK" if success else "Declined")
    else:
        success = bool(result)
        tx_id = None
        status_msg = "OK" if success else "Declined"
    # if payment failed dont charge anything
    if not success:
        return {
            "success": False,
            "status": status_msg,
            "transaction_id": tx_id,
            "amount_charged": 0.0,
        }
    # payment successful 
    return {
        "success": True,
        "status": status_msg,
        "transaction_id": tx_id,
        "amount_charged": amount,
    }

def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway,) -> Dict[str, Any]:
    # validate transaction ID
    if not transaction_id or not transaction_id.strip():
        return {"success": False, "status": "Invalid transaction ID"}
    # validate amount
    if amount <= 0:
        return {"success": False, "status": "Invalid refund amount"}
    if amount > MAX_FEE:
        return {"success": False, "status": "Refund amount exceeds maximum allowed"}
    # call external gateway
    try:
        result = payment_gateway.refund_payment(transaction_id, amount)
    except Exception as exc:
        return {"success": False, "status": f"Refund error: {exc}"}
    # normalize results
    if isinstance(result, dict):
        success = bool(result.get("success"))
        status_msg = result.get("message", "OK" if success else "Declined")
    else:
        success = bool(result)
        status_msg = "OK" if success else "Declined"

    return {"success": success, "status": status_msg}