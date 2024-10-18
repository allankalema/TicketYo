from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),
    path('verify_email/<int:pk>/', views.user_verify_email, name='user_verify_email'),
    path('home/', views.user_home, name='customer_home'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('update-customer/', views.update_customer, name='update_customer'),
]
