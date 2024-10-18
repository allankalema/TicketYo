from django.contrib import admin
from .models import AgentEventAssignment

class AgentEventAssignmentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'event', 'vendor', 'generating_tickets', 'verifying_tickets', 'created_at', 'updated_at')
    search_fields = ('agent__username', 'event__title', 'vendor__username')
    list_filter = ('generating_tickets', 'verifying_tickets', 'vendor')

admin.site.register(AgentEventAssignment, AgentEventAssignmentAdmin)
