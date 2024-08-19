from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update/', views.update_vendor, name='update_vendor'),
    path('delete/', views.delete_vendor, name='delete_vendor'),
    path('change-password/', views.change_password, name='change_password'),
    path('verify_email/<int:pk>/', views.verify_email, name='verify_email'),
]
