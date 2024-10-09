from django.db import models
from vendors.models import Vendor
from events.models import Event

class POSAgent(models.Model):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='pos_agents')
    assigned_events = models.ManyToManyField(Event, related_name='assigned_agents')
    is_active = models.BooleanField(default=True)
    password = models.CharField(max_length=6)
    is_posagent = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
