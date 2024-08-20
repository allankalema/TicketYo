from django.contrib import admin
from .models import Event, TicketCategory

class TicketCategoryInline(admin.TabularInline):
    model = TicketCategory
    extra = 1

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'category', 'start_date', 'end_date', 'venue_name', 'regular_price', 'sale_price', 'inventory', 'tickets_available')
    list_filter = ('category', 'start_date', 'end_date', 'inventory')
    search_fields = ('title', 'description', 'venue_name', 'vendor__username', 'category')

    inlines = [TicketCategoryInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(vendor=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.vendor_id:
            obj.vendor = request.user
        obj.save()

admin.site.register(Event, EventAdmin)
