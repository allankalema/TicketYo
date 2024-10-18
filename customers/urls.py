from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.customer_signup, name='customer_signup'),
    path('verify-email/<int:pk>/', views.customer_verify_email, name='customer_verify_email'),
    path('home/', views.user_home, name='customer_home'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('update-customer/', views.update_customer, name='update_customer'),
]
