from django.contrib import admin
from .models import Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'event', 'user', 'customer_username', 'ticket_category', 'purchase_date', 'verified', 'entity_type')
    list_filter = ('verified', 'entity_type', 'event', 'user')
    search_fields = ('ticket_number', 'customer_username', 'user__username', 'event__title')
    ordering = ('-purchase_date',)
    readonly_fields = ('qr_code', 'purchase_date')  # QR code and purchase date should be read-only

    def get_queryset(self, request):
        # Optionally limit the queryset for admin users
        queryset = super().get_queryset(request)
        return queryset.select_related('event', 'user', 'ticket_category')  # Optimize related fields loading

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return f'<img src="{obj.qr_code.url}" style="width: 150px; height: auto;" />'
        return "No QR Code"
    qr_code_preview.allow_tags = True
    qr_code_preview.short_description = 'QR Code'

    # Optionally, you can add additional actions here for bulk operations
    actions = ['mark_as_verified']

    def mark_as_verified(self, request, queryset):
        queryset.update(verified=True)
        self.message_user(request, "Selected tickets marked as verified.")

    mark_as_verified.short_description = "Mark selected tickets as verified"

# Register the Ticket model with the custom admin class
admin.site.register(Ticket, TicketAdmin)
