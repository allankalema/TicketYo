# customers/admin.py
from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username','email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_customer')
    search_fields = ('username','email', 'first_name', 'last_name', 'is_active')