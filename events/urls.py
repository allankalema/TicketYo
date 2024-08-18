from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    # Define vendor-related URL patterns here in the future.
]
