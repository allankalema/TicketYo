from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'storename', 'store_phone')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'storename', 'store_phone')
    list_filter = ('is_active',)

# @admin.register(ActionLog)
# class ActionLogAdmin(admin.ModelAdmin):
#     list_display = ('admin_user', 'event', 'action', 'timestamp')
#     search_fields = ('admin_user__username', 'event__title', 'action')
#     list_filter = ('action', 'timestamp')
