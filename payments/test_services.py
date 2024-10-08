# payments/test_services.py
from django.test import TestCase
from .services import deposit_money
from django.conf import settings

class DepositMoneyIntegrationTestCase(TestCase):

    def test_deposit_money_integration(self):
        # Replace with actual test values
        msisdn = "256785048264"  # Replace with a valid number for testing
        amount = 1000  # Replace with the desired amount
        narration = "Deposit to account"
        reference = "test_ref_123"

        # Call the deposit_money function
        result = deposit_money(msisdn, amount, narration, reference)

        # Check the response format and values
        self.assertIn("status", result)
        self.assertEqual(result["msisdn"], msisdn)
        self.assertEqual(result["amount"], amount)
        self.assertIn("receipt_number", result)
        self.assertIn("reference_code", result)
