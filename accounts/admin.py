# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_vendor', 'is_customer', 'is_posagent', 'is_staff', 'is_active')
    list_filter = ('is_vendor', 'is_customer', 'is_posagent', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # The fields to be used in editing the User model.
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'storename', 'store_phone', 'is_verified', 'verification_code', 'verification_code_created_at')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_vendor', 'is_customer', 'is_posagent')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password', 'is_vendor', 'is_customer', 'is_posagent', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'password':
            field.error_messages = {'required': 'Please enter a password.'}
        return field

    def save_model(self, request, obj, form, change):
        # Ensure all required fields are filled
        if not obj.username or not obj.email or not obj.first_name or not obj.last_name:
            form.add_error(None, "Please fill in all required fields.")
            return  # Stop saving if there are errors

        if not change:  # New user creation
            if not form.cleaned_data.get('password'):
                form.add_error('password', "Password cannot be empty.")
                return  # Stop saving if there are errors
            
            obj.set_password(form.cleaned_data['password'])  # Hash the password

        super().save_model(request, obj, form, change)  # Call the base class method

    # Optionally, you can add additional actions here for bulk operations
    # actions = ['some_action_here']

# Register the User model with the custom admin class
admin.site.register(User, UserAdmin)
