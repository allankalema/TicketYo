from django.contrib import admin
from .models import POSAgent
from django.db.models import Q

class AssignedEventsInline(admin.TabularInline):
    model = POSAgent.assigned_events.through  # This allows displaying assigned events in the admin interface

class POSAgentAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'vendor', 'is_active')  # Fields to display
    list_filter = ('vendor', 'is_active')  # Filter options
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Search functionality
    inlines = [AssignedEventsInline]  # Inline for managing assigned events

# Register the POSAgent model with its custom admin interface
admin.site.register(POSAgent, POSAgentAdmin)
