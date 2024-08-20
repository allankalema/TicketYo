from django.contrib import admin
from .models import Event, TicketCategory

# Register the Event model
class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1  # Allows adding one extra TicketCategory inline in the admin

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'start_date', 'end_date', 'tickets_available', 'regular_price', 'sale_price')
    list_filter = ('category', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'venue_name', 'vendor__storename')
    inlines = [TicketCategoryInline]


# Register the models with the admin site
admin.site.register(Event, EventAdmin)
admin.site.register(TicketCategory)

