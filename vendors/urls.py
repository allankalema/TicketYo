from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),  # User signup
    path('verify_email/<int:pk>/', views.verify_email, name='verify_email'),  # Email verification
    # path('login/', views.login_view, name='login'),  # User login
    # path('logout/', views.logout_view, name='logout'),  # User logout
    path('dashboard/', views.vendor_dashboard, name='dashboard'),  # Vendor dashboard
    path('inventory/', views.view_inventory, name='view_inventory'),  # View inventory
    path('receipt/<int:ticket_id>/', views.ticket_receipt, name='ticket_receipt'),  # View ticket receipt
    path('vendor/pending-events/', views.pending_events, name='pending_events'),  # View pending events
    path('events-confirmed/', views.events_confirmed_view, name='events_confirmed'),  # Confirmed events
    path('profile/update/', views.update_vendor_profile, name='update_vendor_profile'),
    # path('change-password/', views.change_password, name='change_password'),  # Change password
    # path('password-reset/', views.vendor_password_reset_request, name='vendor_password_reset_request'),  # Password reset request
    # path('password-reset/verify/<uidb64>/', views.vendor_password_reset_verify, name='vendor_password_reset_verify'),  # Password reset verify
    # path('password-reset/confirm/<uidb64>/', views.vendor_password_reset_confirm, name='vendor_password_reset_confirm'),  # Password reset confirm
]
