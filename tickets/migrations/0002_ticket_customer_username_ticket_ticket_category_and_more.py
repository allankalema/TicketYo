# Generated by Django 5.0 on 2024-10-17 11:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='customer_username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.ticketcategory'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='entity_type',
            field=models.CharField(choices=[('customer', 'Customer'), ('vendor', 'Vendor'), ('pos_agent', 'pos_agent')], max_length=10),
        ),
    ]
