# tickets/models.py

from django.db import models
from events.models import Event, TicketCategory
from accounts.models import User
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files import File

# tickets/models.py
class Ticket(models.Model):
    ENTITY_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('pos_agent', 'pos_agent'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, null=True, blank=True)
    customer_username = models.CharField(max_length=255, blank=True, null=True)  # Buyer info
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')  # Vendor info
    ticket_number = models.CharField(max_length=20, unique=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    entity_type = models.CharField(max_length=10, choices=ENTITY_TYPE_CHOICES)  # Buyer type
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_tickets')  # POS Agent info for verification
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_tickets')


    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.ticket_number)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        file_name = f'{self.ticket_number}.png'
        self.qr_code.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.ticket_number} - {self.event.title}'

    @staticmethod
    def generate_ticket_number(event, vendor, category, entity, entity_type):
        from random import randint

        vendor_code = vendor.storename[0].upper()  # Vendor code
        vendor_id = str(vendor.id).zfill(4)        # Vendor ID
        event_code = event.title[0].upper()        # Event code
        event_id = str(event.id).zfill(4)          # Event ID
        category_code = category.category_title[:2].upper() if category else "OR"  # Category code
        category_id = str(category.id).zfill(2) if category else "00"  # Category ID

        # Entity (buyer) details
        entity_code = entity.username[0].upper()   # Buyer username
        entity_id = str(entity.id).zfill(4)        # Buyer ID

        random_digits = str(randint(1000, 9999))   # Random digits for uniqueness

        return f'{vendor_code}{vendor_id}{event_code}{event_id}{category_code}{category_id}{entity_code}{entity_id}{random_digits}'