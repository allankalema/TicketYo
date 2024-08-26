# customers/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', CustomerSignupView.as_view(), name='customer_signup'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('home/', CustomerHomeView.as_view(), name='customer_home'),
    path('logout/', CustomerLogoutView.as_view(), name='customer_logout'),
    path('verify-email/<int:pk>/', CustomerVerifyEmailView.as_view(), name='customer_verify_email'),
]
