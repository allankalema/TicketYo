# Generated by Django 5.0 on 2024-10-17 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('storename', models.CharField(blank=True, max_length=50, null=True)),
                ('store_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('verification_code', models.CharField(blank=True, max_length=6, null=True)),
                ('verification_code_created_at', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_vendor', models.BooleanField(default=False)),
                ('is_customer', models.BooleanField(default=False)),
                ('is_posagent', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]