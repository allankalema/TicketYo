from django.urls import path
from .views import (
    CustomerSignupView,
    CustomerLoginView,
    CustomerLogoutView,
    CustomerHomeView,
    CustomerUpdateView,
    CustomerDeleteView,
    CustomerPasswordChangeView,
    CustomerVerifyEmailView,
)

urlpatterns = [
    path('signup/', CustomerSignupView.as_view(), name='customer_signup'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('logout/', CustomerLogoutView.as_view(), name='customer_logout'),
    path('home/', CustomerHomeView.as_view(), name='customer_home'),
    path('update/', CustomerUpdateView.as_view(), name='customer_update'),
    path('delete/', CustomerDeleteView.as_view(), name='customer_delete'),
    path('change-password/', CustomerPasswordChangeView.as_view(), name='customer_change_password'),
    path('verify_email/<int:pk>/', CustomerVerifyEmailView.as_view(), name='customer_verify_email'),
]
