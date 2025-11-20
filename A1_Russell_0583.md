## Project Implementation Status

Name: Vanessa Russell
ID: 20280583

| **Function Name**               | **Implementation Status** | **What is Missing**                       |
|---------------------------------|---------------------------|-----------------------------------------------|
| **add_book_to_catalog**         | Complete                  | n/a                                           |
| **borrow_book_by_patron**       | Partial                   | Borrowing limit (should be `>= 5`), needs to validate that the user is in the system      |
| **return_book_by_patron**       | Partial                   | Should verify the patron actually borrowed the book, validate 6 didgit patron ID, validate the book is in the database, update available copies of the book, record return date, calculate/display late fees |
| **calculate_late_fee_for_book** | Partial                   | Validate 6 digit patron ID, Should verify that the book is in the database, needs to look up the due date for the book, Needs to calculate how many days the book has been borrowed, check if the book is overdue, calculate fees based on overdue days, applying tiered fee structure and max fee limits when calculating, return JSON response with fee amount, days overdue and status  |
| **search_books_in_catalog**     | Partial                   | Validate input, determine and insure search is by title, author or ISBN, check if there is a matching book and return results |
| **get_patron_status_report**    | Partial                   | validate patron 6 digit ID, Should return borrowed books with due dates, total late fees, borrowing count, and history for patron    |



| Function Name               | Test Script Filename     | Test Coverage Summary                         |
|-----------------------------|--------------------------|-----------------------------------------------|
| add_book_to_catalog         | test_add_book.py         | Invalid ISBN too short, missing title, title too long, missing author, author too long, zero copies, negative copies |
| borrow_book_by_patron       | test_borrow_book.py      | Missing patron ID, invalid patron ID format, non-existent book, negative book ID |
| return_book_by_patron       | test_return_book.py      | Returning a book not borrowed, invalid patron ID, invalid book ID, generic late fee/return response check |
| calculate_late_fee_for_book | test_late_fee.py         | Verifies return type is dict, contains expected keys, ensures non-negative fee and days, and handles invalid patron/book inputs |
| search_books_in_catalog     | test_search_books.py     | Searches by partial title, partial author, exact ISBN match, empty term, and no result |
| get_patron_status_report    | test_patron_status.py    | Ensures return type is dict, allows empty dict or dict with status, and handles invalid/negative patron IDs |

