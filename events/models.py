from django.db import models
from vendors.models import Vendor

class Event(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='events')  # Mandatory, linked to Vendor
    poster = models.ImageField(upload_to='event_posters/')  # Required field
    title = models.CharField(max_length=200)  # Required field
    description = models.TextField()  # Required field
    category = models.CharField(max_length=100)  # Required field (e.g., "conference", "concert")
    start_date = models.DateTimeField()  # Required field
    end_date = models.DateTimeField(null=True, blank=True)  # Optional field
    venue_name = models.CharField(max_length=100)  # Required field
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)  # Required field
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional field
    tickets_available = models.PositiveIntegerField(null=True, blank=True)  # Optional field

    def __str__(self):
        return self.title

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_categories')  # Mandatory, linked to Event
    category_title = models.CharField(max_length=100)  # Required field
    category_price = models.DecimalField(max_digits=10, decimal_places=2)  # Required field
    category_tickets_available = models.PositiveIntegerField()  # Required field

    def __str__(self):
        return f'{self.category_title} - {self.event.title}'
