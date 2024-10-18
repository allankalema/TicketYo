from django.db import models
from django.conf import settings
from events.models import Event  # Import the Event model from the events app

class AgentEventAssignment(models.Model):
    # ForeignKey to the User model (POS agent), with a unique related_name
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pos_agent_events')
    
    # ForeignKey to the Event model in the events app
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='agent_assignments')

    # Boolean fields for permissions
    generating_tickets = models.BooleanField(default=False)
    verifying_tickets = models.BooleanField(default=False)

    # Optional: Add timestamps for tracking assignments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.username} - {self.event.title} (Generating: {self.generating_tickets}, Verifying: {self.verifying_tickets})"
