import requests
from django.conf import settings

def deposit_mobile_money(msisdn, amount, narration, reference):
    url = settings.API_URL.strip()  # Ensure no trailing spaces
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "username": settings.API_USERNAME,
        "password": settings.API_PASSWORD,
        "api": "depositmobilemoney",
        "msisdn": msisdn,
        "amount": amount,
        "narration": narration,
        "reference": reference,
        "status_notification_url": "https://yourapp.com/status-handler/"
    }

    response = requests.post(url, json=data, headers=headers)
    print("Raw Response:", response.text)  # For debugging
    return response.json()  # Parse the response as JSON
