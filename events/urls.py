from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.vendor_events, name='vendor_events'),
    path('', views.all_events, name='all_events'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/update/', views.update_event, name='update_event'),
    # path('event/<int:event_id>/add/', views.add_to_cart, name='add_to_cart'),
    # path('cart/', views.view_cart, name='view_cart'),
    # path('cart/<int:cart_item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
     path('vendor-event/<int:event_id>/', views.event_detail_view, name='vendor_event_detail'),
    path('past-events/', views.past_events_view, name='past_events'),
    path('approve-event/<int:event_id>/', views.dash_approve_event, name='dash_approve_event'),
    path('home/',views.homepage, name='homepage'),
]
