# payments/urls.py
from django.urls import path
from .views import deposit_view

urlpatterns = [
    path('deposit/', deposit_view, name='deposit_money'),
]
