# payments/views.py
from django.http import JsonResponse
from django.shortcuts import render
from .services import deposit_money

def deposit_view(request):
    if request.method == 'POST':
        msisdn = request.POST.get('msisdn')
        amount = request.POST.get('amount')
        narration = request.POST.get('narration')

        # Ensure amount is an integer
        try:
            amount = int(amount)
        except ValueError:
            return JsonResponse({"error": "Invalid amount"}, status=400)

        # Call the deposit_money function and get the result
        result = deposit_money(msisdn, amount, narration)

        # If the result has an error, return that error
        if 'error' in result:
            return JsonResponse(result, status=400)

        # Otherwise, return the successful result
        return JsonResponse(result)

    # For GET request, render the deposit form
    return render(request, 'payments/deposit.html')
