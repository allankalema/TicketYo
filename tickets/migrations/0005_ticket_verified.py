# Generated by Django 5.1 on 2024-08-30 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_ticket_entity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]