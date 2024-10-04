# payments/services.py
import requests
import json

BLINK_API_URL = "https://payments.blink.co.ug/api/"  # Live URL
USERNAME = "4627252e-909cdfae-abc09f56-3497cca4"
PASSWORD = "gf3rx57lMxCG3i243dFWNlTKYjpGou9PuRUy"

# Function to make deposit
def deposit_mobile_money(msisdn, amount, narration, reference, status_notification_url=""):
    url = BLINK_API_URL
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "api": "depositmobilemoney",
        "msisdn": msisdn,
        "amount": amount,
        "narration": narration,
        "reference": reference,
        "status_notification_url": status_notification_url or "https://example.com/status-handler/"  # Provide a default URL
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()

def withdraw_mobile_money(msisdn, amount, narration, reference, status_notification_url=""):
    url = BLINK_API_URL
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "api": "withdrawmobilemoney",
        "msisdn": msisdn,
        "amount": amount,
        "narration": narration,
        "reference": reference,
        "status_notification_url": status_notification_url or "https://example.com/status-handler/"  # Default URL
    }
    
    headers = {"Content-Type": "application/json"}
    
    # Send the request to the API
    response = requests.post(url, json=payload, headers=headers)  # Use 'json=' instead of 'data=json.dumps(payload)'

    return response.json()


# Function to check transaction status
def check_transaction_status(reference_code):
    url = BLINK_API_URL
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "api": "checktransactionstatus",
        "reference_code": reference_code,
    }

    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    return response.json()

def check_network_status(msisdn):
    url = BLINK_API_URL
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "api": "checknetworkstatus",
        "msisdn": msisdn,
        "service": "MOBILE MONEY"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"message": str(e), "error": True}
    except requests.exceptions.RequestException as e:
        return {"message": "Network error occurred", "error": True}

