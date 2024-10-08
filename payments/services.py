import requests
import time  # Add this import
from django.conf import settings
from datetime import datetime

def deposit_money(msisdn, amount, narration, reference=None):
    url = settings.BLINK_API_URL
    status_notification_url = settings.BLINK_STATUS_NOTIFICATION_URL

    payload = {
        "username": settings.BLINK_API_USERNAME,
        "password": settings.BLINK_API_PASSWORD,
        "api": "depositmobilemoney",
        "msisdn": msisdn,
        "amount": amount,
        "narration": narration,
        "reference": reference,
        "status_notification_url": status_notification_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Start timing the API call
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers)
    elapsed_time = time.time() - start_time
    print(f"Blink API call took {elapsed_time:.2f} seconds")  # Log the response time

    if response.status_code == 200:
        response_data = response.json()
        
        result = {
            "status": response_data.get("status"),
            "msisdn": msisdn,
            "initiation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "completion_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # To be updated via notification
            "amount": amount,
            "receipt_number": response_data.get("receipt_number"),
            "reference_code": response_data.get("reference_code")
        }

        return result

    else:
        return {
            "error": "Failed to process the deposit request",
            "status_code": response.status_code,
            "details": response.text
        }



def check_transaction_status(reference_code):
    """Polls the Blink API to check the status of a transaction."""
    url = settings.BLINK_API_URL
    payload = {
        "username": settings.BLINK_API_USERNAME,
        "password": settings.BLINK_API_PASSWORD,
        "api": "checktransactionstatus",
        "reference_code": reference_code
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def poll_transaction_status(reference_code, max_attempts=5, interval=5):
    """Polls the transaction status until it is no longer pending or max attempts are reached."""
    for attempt in range(max_attempts):
        status_data = check_transaction_status(reference_code)
        status = status_data.get("status")

        if status and status != "PENDING":
            return status_data  # Return as soon as a final status is found
        time.sleep(interval)  # Wait for the specified interval before polling again
    return {"status": "PENDING", "message": "Transaction status not finalized after polling."}
