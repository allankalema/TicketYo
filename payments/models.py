# payments/models.py
from django.db import models
from django.conf import settings
from customers.models import Customer  # Import Customer model
from vendors.models import Vendor      # Import Vendor model
from events.models import Event        # Import Event model

class Payment(models.Model):
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)  # Track if customer or vendor
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to Customer or Vendor
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Link to the event
    ticket_category = models.CharField(max_length=100)  # To store the category of the ticket
    msisdn = models.CharField(max_length=15)  # Mobile Money Number
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount paid
    reference = models.CharField(max_length=100)  # Transaction reference
    narration = models.TextField(blank=True, null=True)  # Additional info about the transaction
    timestamp = models.DateTimeField(auto_now_add=True)  # Time the payment was made
    payment_status = models.CharField(max_length=20, default='PENDING')  # Status of the payment (e.g., PENDING, SUCCESSFUL, FAILED)

    def __str__(self):
        return f"Payment {self.reference} by {self.user.username} for {self.event.title}"

