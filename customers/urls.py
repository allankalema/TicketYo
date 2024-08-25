from django.urls import path
from .views import CustomerSignupView, CustomerLoginView, customer_home, logout_view

urlpatterns = [
    path('signup/', CustomerSignupView.as_view(), name='customer_signup'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('home/', customer_home, name='customer_home'),
    path('logout/', logout_view, name='customer_logout'),
]
