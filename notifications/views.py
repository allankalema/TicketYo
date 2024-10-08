# notifications/views.py
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def blink_status_notification(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Notification received: {data}")  # Log the incoming notification
            
            # Process the Blink API notification data
            result = {
                "status": data.get("status"),
                "msisdn": data.get("msisdn"),
                "initiation_date": data.get("initiation_date"),
                "completion_date": data.get("completion_date"),
                "amount": data.get("amount"),
                "receipt_number": data.get("receipt_number"),
                "reference_code": data.get("reference_code")
            }

            # Log the result for debugging
            logger.info(f"Processed result: {result}")

            return JsonResponse(result, status=200)
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)
