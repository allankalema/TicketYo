# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.make_deposit, name='make_deposit'),
    path('withdraw/', views.make_withdrawal, name='make_withdrawal'),
    path('check-status/', views.check_status, name='check_status'),
]
