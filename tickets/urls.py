# tickets/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:event_id>/', views.buy_ticket, name='buy_ticket'),
    path('buy_ticket/<int:event_id>/', views.buy_ticket, name='buy_ticket'),
    path('view_qr_codes/<int:event_id>/', views.view_qr_codes, name='view_qr_codes'),
    path('verifiable-events/', views.verifiable_events, name='verifiable_events'),
    path('verify-ticket/<int:event_id>/', views.verify_ticket, name='verify_ticket'),
    path('download_ticket/<str:ticket_number>/', views.download_ticket_pdf, name='download_ticket_pdf'),
]
