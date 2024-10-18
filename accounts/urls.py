# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.custom_login, name='universal_login'),
     path('logout/', views.universal_logout, name='universal_logout'),
     path('change-password/', views.change_password, name='change_password'),
     path('cart/add/<int:event_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('delete-account/', views.delete_user_view, name='delete_account'),
    # Other URLs...
]
