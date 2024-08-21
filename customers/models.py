# customers/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    # Use related_name to avoid conflicts with the Vendor model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_set',  # Update related_name to be unique
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_permissions_set',  # Update related_name to be unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username
