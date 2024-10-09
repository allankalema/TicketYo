from django.urls import path
from .views import manage_pos_agents

urlpatterns = [
    path('manage_agents/', manage_pos_agents, name='manage_pos_agents'),
]
