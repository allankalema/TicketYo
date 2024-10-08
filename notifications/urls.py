# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('status-notification/', views.blink_status_notification, name='blink_status_notification'),
]
