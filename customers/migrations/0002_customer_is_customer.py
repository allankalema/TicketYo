# Generated by Django 5.1 on 2024-08-25 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='is_customer',
            field=models.BooleanField(default=True),
        ),
    ]