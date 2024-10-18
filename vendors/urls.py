from django.urls import path
from . import views

urlpatterns = [
   path('signup/', views.vendor_signup, name='vendor_signup'),
    path('verify-email/<int:pk>/', views.vendor_verify_email, name='vendor_verify_email'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),  # Vendor dashboard
    path('inventory/', views.view_inventory, name='view_inventory'),  # View inventory
    path('receipt/<int:ticket_id>/', views.ticket_receipt, name='ticket_receipt'),  # View ticket receipt
    path('vendor/pending-events/', views.pending_events, name='pending_events'),  # View pending events
    path('events-confirmed/', views.events_confirmed_view, name='events_confirmed'),  # Confirmed events
    path('profile/update/', views.update_vendor_profile, name='update_vendor_profile'),
]
