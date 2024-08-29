from django.contrib import admin

# Register your models here.
# tickets/admin.py

from django.contrib import admin
from .models import Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'event', 'ticket_category', 'customer_username', 'vendor', 'purchase_date','entity_type')
    search_fields = ('ticket_number', 'event__title', 'customer__username', 'vendor__storename')
    list_filter = ('event', 'ticket_category', 'vendor', 'purchase_date')
    ordering = ('-purchase_date',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If it's a new object
            obj.ticket_number = Ticket.generate_ticket_number(
                event=obj.event,
                vendor=obj.vendor,
                category=obj.ticket_category,
                customer=obj.customer
            )
        super().save_model(request, obj, form, change)

admin.site.register(Ticket, TicketAdmin)
