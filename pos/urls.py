from django.urls import path
from .views import *

urlpatterns = [
    path('manage_agents/', manage_pos_agents, name='manage_pos_agents'),
    path('create_agent/', create_pos_agent, name='create_pos_agent'),
    path('agent_detail/<int:agent_id>/', agent_detail, name='agent_detail'),
]
