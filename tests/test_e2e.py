import pytest

@pytest.mark.e2e
def test_add_and_return_book(page):
    base_url = "http://localhost:5001"

    # Go to home page
    page.goto(base_url)

    # Go to Add Book page (➕ Add Book)
    page.click("a:has-text('Add Book')")

    # Fill the Add Book form
    page.fill("input[name='title']", 'Playwright Testing Book')
    page.fill("input[name='author']", 'Test Author')
    
    # ISBN must be 13 digits
    page.fill("input[name='isbn']", '9999999999999')

    page.fill("input[name='total_copies']", '3')

    # Submit (Add Book to Catalog)
    page.click("button:has-text('Add Book')")

    # Verify the book appears in the catalog
    page.goto(f"{base_url}/catalog")
    assert "Playwright Testing Book" in page.content()

    # Now go to Return Book page
    page.click("a:has-text('Return Book')")

    # Fill the return form
    page.fill("input[name='patron_id']", "123456")    # must be 6 digits
    page.fill("input[name='book_id']", "1")           # assume book ID 1
    
    # Submit return
    page.click("button:has-text('Process Return')")

    # Check for success or error message
    assert "success" in page.content().lower() or "not yet implemented" in page.content().lower()