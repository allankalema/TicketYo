from django.db import models

class Vendor(models.Model):
    class Meta:
        managed = False  # Prevent Django from trying to create or manage a table for this model
