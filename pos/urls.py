from django.urls import path
from .views import *

urlpatterns = [
    path('manage_agents/', manage_pos_agents, name='manage_pos_agents'),
    path('create_agent/', create_pos_agent, name='create_pos_agent'),
    path('agent_detail/<int:agent_id>/', agent_detail, name='agent_detail'),
    path('agent_action/<int:agent_id>/', agent_action, name='agent_action'), 
    path('event_detail/<int:event_id>/', pos_event_detail, name='pos_event_detail'), 
    path('verify-email/', verify_email, name='verify_email'),
    path('signup/<str:email>/', signup_pos_agent, name='signup_pos_agent'),
    # path('pos/login/', pos_agent_login, name='pos_agent_login'),
    path('pos/dashboard/', pos_dashboard, name='pos_dashboard'), # Detail view for agent
]
