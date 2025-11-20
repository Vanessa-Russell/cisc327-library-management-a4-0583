from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

def test_pay_late_fees_successful_payment(mocker):
    # Pretend the book exists
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 1, "title": "Test Book"},
    )
    # Pretend the late fee is $5.00
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 5.0, "days_overdue": 10, "status": "OK"},
    )
    # mock external payment gateway (simulated)
    gateway_mock = Mock(spec=PaymentGateway)
    gateway_mock.process_payment.return_value = {
        "success": True,
        "transaction_id": "TX123",
        "message": "Payment processed successfully",
    }
    # Call the function under test
    result = pay_late_fees("123456", 1, gateway_mock)
    # Verify that process_payment was called correctly
    gateway_mock.process_payment.assert_called_once_with("123456", 5.0)
    # Verify the result
    assert result["success"] is True
    assert result["transaction_id"] == "TX123"
    assert result["amount_charged"] == 5.0

def test_pay_late_fees_declined_payment(mocker):
    # Pretend the book exists
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 2, "title": "Declined Book"},
    )
    # Pretend the late fee is $10
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 10.0, "days_overdue": 5, "status": "OK"},
    )
    # Payment gateway returns a DECLINED transaction
    gateway_mock = Mock(spec=PaymentGateway)
    gateway_mock.process_payment.return_value = {
        "success": False,
        "transaction_id": None,
        "message": "Card declined – insufficient funds",
    }
    # Call the function under test
    result = pay_late_fees("123456", 2, gateway_mock)
    # Verify that the gateway was called with correct arguments
    gateway_mock.process_payment.assert_called_once_with("123456", 10.0)
    # Verify the output reflects the decline
    assert result["success"] is False
    assert "declined" in result["status"].lower()
    assert result["transaction_id"] is None

def test_pay_late_fees_invalid_patron_id_does_not_call_gateway(mocker):
    # We patch these DB functions, but they should not be used because
    # the function will return early due to invalid patron ID.
    mocker.patch("services.library_service.get_book_by_id")
    mocker.patch("services.library_service.calculate_late_fee_for_book")

    gateway_mock = Mock(spec=PaymentGateway)
    # Invalid patron ID: not 6 digits
    result = pay_late_fees("ABC123", 1, gateway_mock)
    # Payment gateway must not be called
    gateway_mock.process_payment.assert_not_called()
    # Result should indicate failure due to invalid patron ID
    assert result["success"] is False
    assert "invalid patron" in result["status"].lower()

def test_pay_late_fees_zero_fee_does_not_call_gateway(mocker):
    # book exists
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 3, "title": "No Fee Book"},
    )
    # late fee calculation returns zero
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "OK"},
    )
    gateway_mock = Mock(spec=PaymentGateway)
    result = pay_late_fees("123456", 3, gateway_mock)
    # Because fee is zero, the gateway must not be called
    gateway_mock.process_payment.assert_not_called()
    # Function should succeed but charge nothing
    assert result["success"] is True
    assert result["amount_charged"] == 0.0
    assert "no late fees" in result["status"].lower()

def test_pay_late_fees_network_error_handled(mocker):
    # book exists
    mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={"id": 4, "title": "Network Error Book"},
    )
    # non-zero late fee so that we actually call the gateway
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 3.0, "days_overdue": 2, "status": "OK"},
    )
    gateway_mock = Mock(spec=PaymentGateway)
    # Simulate a network failure inside the payment gateway
    gateway_mock.process_payment.side_effect = RuntimeError("Network down")
    result = pay_late_fees("123456", 4, gateway_mock)
    # Gateway should have been called once, then raised the error
    gateway_mock.process_payment.assert_called_once_with("123456", 3.0)
    # Function should handle the error gracefully
    assert result["success"] is False
    assert "error" in result["status"].lower()

def test_refund_late_fee_success(mocker):
    gateway_mock = Mock(spec=PaymentGateway)
    gateway_mock.refund_payment.return_value = {
        "success": True,
        "message": "Refund approved",
    }
    result = refund_late_fee_payment("TX123", 10.0, gateway_mock)
    # Gateway should be called exactly once with these parameters
    gateway_mock.refund_payment.assert_called_once_with("TX123", 10.0)
    # Function should report success
    assert result["success"] is True
    assert "approved" in result["status"].lower()

def test_refund_late_fee_invalid_amounts_negative_zero_exceeds_max(mocker):
    gateway_mock = Mock(spec=PaymentGateway)
    # Negative amount
    result_neg = refund_late_fee_payment("TX1", -1.0, gateway_mock)
    # Zero amount
    result_zero = refund_late_fee_payment("TX1", 0.0, gateway_mock)
    # Exceeds $15 max
    result_excess = refund_late_fee_payment("TX1", 16.0, gateway_mock)
    # None of these should call the gateway
    gateway_mock.refund_payment.assert_not_called()
    assert result_neg["success"] is False
    assert "invalid refund amount" in result_neg["status"].lower()
    assert result_zero["success"] is False
    assert "invalid refund amount" in result_zero["status"].lower()
    assert result_excess["success"] is False
    assert "exceeds" in result_excess["status"].lower()

def test_pay_late_fees_invalid_book_id_does_not_call_gateway(mocker):
    gateway_mock = Mock(spec=PaymentGateway)
    result = pay_late_fees("123456", 0, gateway_mock)  # invalid book_id
    gateway_mock.process_payment.assert_not_called()
    assert result["success"] is False
    assert "invalid book id" in result["status"].lower()

def test_pay_late_fees_book_not_found_does_not_call_gateway(mocker):
    # book lookup returns None
    mocker.patch("services.library_service.get_book_by_id", return_value=None)
    gateway_mock = Mock(spec=PaymentGateway)
    result = pay_late_fees("123456", 999, gateway_mock)
    gateway_mock.process_payment.assert_not_called()
    assert result["success"] is False
    assert "book not found" in result["status"].lower()

def test_refund_late_fee_gateway_error_handled(mocker):
    gateway_mock = Mock(spec=PaymentGateway)
    gateway_mock.refund_payment.side_effect = RuntimeError("Network down")
    result = refund_late_fee_payment("TX123", 10.0, gateway_mock)
    gateway_mock.refund_payment.assert_called_once_with("TX123", 10.0)
    assert result["success"] is False
    assert "error" in result["status"].lower()