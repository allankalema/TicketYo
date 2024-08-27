# tickets/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:event_id>/', views.buy_ticket, name='buy_ticket'),
    # Other ticket-related paths...
]
