from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('update/', views.update_vendor, name='update_vendor'),
    path('delete/', views.delete_vendor, name='delete_vendor'),
    path('change-password/', views.change_password, name='change_password'),
    path('verify_email/<int:pk>/', views.verify_email, name='verify_email'),
    path('password-reset/', views.vendor_password_reset_request, name='vendor_password_reset_request'),
    path('password-reset/verify/<uidb64>/', views.vendor_password_reset_verify, name='vendor_password_reset_verify'),
    path('password-reset/confirm/<uidb64>/', views.vendor_password_reset_confirm, name='vendor_password_reset_confirm'),
    path('inventory/', views.view_inventory, name='view_inventory'),
    path('receipt/<int:ticket_id>/', views.ticket_receipt, name='ticket_receipt'),
]
