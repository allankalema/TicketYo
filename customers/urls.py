# customers/urls.py
from django.urls import path
from .views import CustomerLoginView, CustomerSignupView, CustomerHomeView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('signup/', CustomerSignupView.as_view(), name='customer_signup'),
    path('home/', CustomerHomeView.as_view(), name='customer_home'),
    path('logout/', LogoutView.as_view(), name='customer_logout'),  # Logout URL
]

