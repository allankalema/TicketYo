from django.shortcuts import render
from django.http import JsonResponse
from .services import deposit_mobile_money, withdraw_mobile_money, check_transaction_status, check_network_status

# View for making a deposit
# View for making a deposit
def make_deposit(request):
    if request.method == "POST":
        msisdn = request.POST.get("msisdn")
        amount = request.POST.get("amount")
        narration = request.POST.get("narration", "Payment deposit")
        reference = request.POST.get("reference", "default_reference")
        
        # Step 1: Check if amount is a valid integer
        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({
                "message": "Invalid format for parameter 'amount'. Amount should be a whole number.",
                "error": True
            })
        
        # Step 2: Check the network status of the MSISDN
        network_status = check_network_status(msisdn)
        
        # Step 3: If the network is not ACTIVE, return an error response
        if network_status.get('status') != 'ACTIVE':
            return JsonResponse({
                "message": f"MSISDN '{msisdn}' is not associated with an active network.",
                "error": True
            })
        
        # Step 4: Proceed with deposit if the network is active
        response = deposit_mobile_money(msisdn, amount, narration, reference)
        return JsonResponse(response)
    
    # Render deposit form for GET request
    return render(request, 'payments/deposit.html')


# View for making a withdrawal
def make_withdrawal(request):
    if request.method == "POST":
        msisdn = request.POST.get("msisdn")
        
        # Ensure amount is a valid integer
        try:
            amount = int(request.POST.get("amount"))
        except ValueError:
            return JsonResponse({
                "message": "Invalid format for parameter 'amount'. Amount should be a whole number.",
                "error": True
            })
        
        narration = request.POST.get("narration", "Vendor withdrawal")
        reference = request.POST.get("reference", "default_reference")

        # Proceed with withdrawal, ensuring status_notification_url is provided
        response = withdraw_mobile_money(msisdn, amount, narration, reference)
        return JsonResponse(response)
    
    # Render withdrawal form for GET request
    return render(request, 'payments/withdraw.html')


# View for checking the transaction status
def check_status(request):
    if request.method == "GET":
        reference_code = request.GET.get("reference_code")
        
        response = check_transaction_status(reference_code)
        return JsonResponse(response)
    
    # Render the status check form for GET request
    return render(request, 'payments/status.html')
