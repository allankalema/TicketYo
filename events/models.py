from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image

User = get_user_model()

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('Concert', 'Concert'),
        ('Conference', 'Conference'),
        ('Festival', 'Festival'),
        ('Workshop', 'Workshop'),
        ('Sports', 'Sports'),
        ('Theatre', 'Theatre'),
        ('Others', 'Others')
    ]

    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    custom_category = models.CharField(max_length=50, blank=True, null=True, help_text="If 'Others' is selected, specify the category here.")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Optional, only required for multi-day events.")
    venue_name = models.CharField(max_length=255)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Optional sale price.")
    inventory = models.BooleanField(default=False, help_text="Enable if you want to manage inventory (tickets available).")
    tickets_available = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),])

    def clean(self):
        # Ensure sale price is less than regular price
        if self.sale_price and self.sale_price >= self.regular_price:
            raise ValidationError('Sale price must be less than regular price.')

        # Ensure tickets_available is set if inventory is enabled
        if self.inventory and not self.tickets_available:
            raise ValidationError('You must specify the number of tickets available if inventory is enabled.')

        # Validate image resolution
        if self.image:
            img = Image.open(self.image)
            if img.width < 1200 or img.height < 1600:
                raise ValidationError('Image resolution must be at least 1200x1600 pixels.')

    def __str__(self):
        return self.title

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, related_name='ticket_categories', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tickets_available = models.PositiveIntegerField(blank=True, null=True, help_text="Optional, only required if inventory management is enabled.")

    def clean(self):
        if self.event.inventory and not self.tickets_available:
            raise ValidationError('You must specify the number of tickets available for this category if inventory is enabled.')

    def __str__(self):
        return f"{self.title} - {self.event.title}"
