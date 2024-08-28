from django.db import models
from vendors.models import Vendor
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
    tickets_sold = models.PositiveIntegerField(default=0)  # New field to track tickets sold

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
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_user()} - {self.event.title}'
    
    def get_user(self):
        return self.vendor if self.vendor else self.customer
