from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'storename', 'store_phone')
    search_fields = ('username', 'email', 'storename')
    list_filter = ('is_active',)
