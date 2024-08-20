from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.vendor_events, name='vendor_events'),
     path('', views.all_events, name='all_events'),
    # Add other URLs related to events if needed
]
