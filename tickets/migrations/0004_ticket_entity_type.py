# Generated by Django 5.1 on 2024-08-29 19:16

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_remove_ticket_customer_ticket_customer_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='entity_type',
            field=models.CharField(choices=[('customer', 'Customer'), ('vendor', 'Vendor')], default=django.utils.timezone.now, max_length=10),
            preserve_default=False,
        ),
    ]