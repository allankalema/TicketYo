from django.contrib import admin
from .models import POSAgent

class POSAgentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'username', 'is_active')
    list_filter = ('is_active', 'vendor')
    search_fields = ('first_name', 'last_name', 'email', 'username')
    
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'email', 'username', 'vendor', 'assigned_events', 'is_active')
        }),
    )

    # Hide the password field in the admin interface
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['password'].widget = admin.widgets.HiddenInput()
        return form

admin.site.register(POSAgent, POSAgentAdmin)
