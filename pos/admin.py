from django.contrib import admin
from .models import AgentEventAssignment

class AgentEventAssignmentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'event', 'generating_tickets', 'verifying_tickets', 'created_at')
    list_filter = ('generating_tickets', 'verifying_tickets', 'agent', 'event')
    search_fields = ('agent__username', 'event__title')

admin.site.register(AgentEventAssignment, AgentEventAssignmentAdmin)
