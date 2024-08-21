from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.vendor_events, name='vendor_events'),
     path('', views.all_events, name='all_events'),
     path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    # Add other URLs related to events if needed
]
