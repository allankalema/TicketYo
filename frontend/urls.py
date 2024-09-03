from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
     path('universal-login/', views.universal_login_view, name='universal_login'),
      path('/forgot_password/', views.forgot_password, name='main-forgot_password'),
]
