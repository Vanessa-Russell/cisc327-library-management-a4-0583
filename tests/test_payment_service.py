from services.payment_service import PaymentGateway

def test_payment_gateway_process_and_refund():
    gateway = PaymentGateway()
    # Call process_payment (simulated)
    result = gateway.process_payment("123456", 5.0)
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "transaction_id" in result
    # Call refund_payment (simulated)
    refund = gateway.refund_payment(result["transaction_id"], 5.0)
    assert isinstance(refund, dict)
    assert refund["success"] is True