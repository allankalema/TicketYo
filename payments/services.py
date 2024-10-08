# payments/services.py
import requests
from django.conf import settings
from datetime import datetime

# Function to process a deposit request to the Blink API
def deposit_money(msisdn, amount, narration, reference=None):
    # Set the Blink API URL and status notification URL from settings
    url = settings.BLINK_API_URL
    status_notification_url = settings.BLINK_STATUS_NOTIFICATION_URL

    # Prepare the payload for the Blink API request
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

    # Define headers for the request
    headers = {
        "Content-Type": "application/json"
    }

    # Send the POST request to the Blink API
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request to Blink API was successful
    if response.status_code == 200:
        response_data = response.json()
        
        # Create a dictionary with expected output format
        result = {
            "status": response_data.get("status"),
            "msisdn": msisdn,
            "initiation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "completion_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # To be updated via notification
            "amount": amount,
            "receipt_number": response_data.get("receipt_number"),
            "reference_code": response_data.get("reference_code")
        }

        return result  # Return the preliminary result

    else:
        # Handle error responses from the Blink API
        return {
            "error": "Failed to process the deposit request",
            "status_code": response.status_code,
            "details": response.text
        }
