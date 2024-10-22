from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from accounts.models import User  # This remains as is
from django.contrib.auth import get_user_model
from django.utils import timezone

class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    poster = models.ImageField(upload_to='event_posters/')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    venue_name = models.CharField(max_length=100)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tickets_available = models.PositiveIntegerField(null=True, blank=True)
    tickets_sold = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    adminaction = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, editable=False)

    def is_sold_out(self):
        return self.tickets_available is not None and self.tickets_sold >= self.tickets_available

    def __str__(self):
        return self.title

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_categories')  # Mandatory, linked to Event
    category_title = models.CharField(max_length=100)  # Required field
    category_price = models.DecimalField(max_digits=10, decimal_places=2)  # Required field
    category_tickets_available = models.PositiveIntegerField()  # Required field
    category_tickets_sold = models.PositiveIntegerField(default=0)  # New field to track tickets sold in this category

    def is_category_sold_out(self):
        return self.category_tickets_sold >= self.category_tickets_available

    def __str__(self):
        return f'{self.category_title} - {self.event.title}'

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)  # Make event optional
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.event.title if self.event else "No Event"}'
  
    
class ActionLog(models.Model):
    admin_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Link to the user who performed the action
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Direct reference to Event model
    action = models.CharField(max_length=50)  # E.g., 'approved' or 'rejected'
    timestamp = models.DateTimeField(default=timezone.now)  # Time of the action

    def __str__(self):
        return f"{self.admin_user} {self.action} {self.event.title} at {self.timestamp}"