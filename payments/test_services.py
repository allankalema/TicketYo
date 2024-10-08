# payments/test_services.py
from django.test import TestCase
from .services import deposit_money, poll_transaction_status

class DepositMoneyIntegrationTestCase(TestCase):

    def test_deposit_money_integration(self):
        msisdn = "256785048264"
        amount = 500
        narration = "Deposit to account"
        reference = "test_ref_123"

        # Step 1: Initiate the deposit
        initial_result = deposit_money(msisdn, amount, narration, reference)
        reference_code = initial_result.get("reference_code")
        
        # Step 2: Poll for the final status
        if reference_code:
            final_result = poll_transaction_status(reference_code)
            print("Final transaction result:", final_result)
            self.assertIn("status", final_result)
            self.assertIn("reference_code", final_result)
            self.assertEqual(final_result["reference_code"], reference_code)
