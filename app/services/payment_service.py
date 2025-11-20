from typing import Dict

class PaymentGateway:

    def process_payment(self, patron_id: str, amount: float) -> Dict:
        return {
            "success": True,
            "transaction_id": "SIMULATED_TXN_ID",
            "message": "Payment processed (simulated).",
        }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict:
        return {
            "success": True,
            "message": f"Refund of ${amount:.2f} processed (simulated).",
        }