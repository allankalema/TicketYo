from django.contrib import admin
from .models import Event, TicketCategory, Cart, ActionLog

class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1  # Number of empty forms to display

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'end_date', 'regular_price', 'sale_price', 'tickets_available', 'status')
    list_filter = ('status', 'category', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'venue_name')
    inlines = [TicketCategoryInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # If the object already exists
            return ['adminaction']
        return []

class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_title', 'event', 'category_price', 'category_tickets_available', 'category_tickets_sold')
    list_filter = ('event',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'added_at')
    list_filter = ('user', 'event')

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'event', 'action', 'timestamp')
    list_filter = ('admin_user', 'event', 'action', 'timestamp')

# Register your models here
admin.site.register(Event, EventAdmin)
admin.site.register(TicketCategory, TicketCategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
