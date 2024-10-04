# payments/admin.py
from django.contrib import admin
from .models import Payment  # Import the Payment model

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'total_amount', 'payment_status', 'timestamp')
    search_fields = ('user__username', 'event__title', 'reference')
    list_filter = ('payment_status', 'user_type')
