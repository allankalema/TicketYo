# # vendors/admin.py
# from django.contrib import admin
# from django.forms.widgets import HiddenInput  # Correct import
# from .models import Vendor

# @admin.register(Vendor)
# class VendorAdmin(admin.ModelAdmin):
#     # List all crucial fields in the admin panel
#     list_display = (
#         'user',  # The related User instance
#         'username',
#         'email',
#         'first_name',
#         'last_name',
#         'storename',
#         'store_phone',
#         'is_active',
#         'is_staff',
#         'is_superuser',
#     )
    
#     # Include search fields for better usability
#     search_fields = (
#         'user__username',
#         'user__email',
#         'user__first_name',
#         'user__last_name',
#         'storename',
#         'store_phone',
#     )
    
#     # Add filtering options for admin panel
#     list_filter = ('is_active', 'is_staff', 'is_superuser')
    
#     # Optional: Customizing the form displayed in the admin panel
#     fieldsets = (
#         (None, {
#             'fields': (
#                 'user',
#                 'username',
#                 'email',
#                 'first_name',
#                 'last_name',
#                 'storename',
#                 'store_phone',
#                 'is_active',
#                 'is_staff',
#                 'is_superuser',
#             ),
#         }),
#     )
    
 