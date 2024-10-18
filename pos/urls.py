from django.urls import path
from . import views

urlpatterns = [
    path('manage_agents/', views.manage_pos_agents, name='manage_pos_agents'),
    path('create_agent/', views.create_pos_agent, name='create_pos_agent'),
    path('agent_action/<int:agent_id>/', views.agent_action, name='agent_action'), 
    path('event_detail/<int:event_id>/', views.pos_event_detail, name='pos_event_detail'), 
    path('verify-email/', views.verify_email, name='verify_email'),
    path('signup/<str:email>/', views.signup_pos_agent, name='signup_pos_agent'),
    path('pos/dashboard/', views.pos_dashboard, name='pos_dashboard'), 

    path('agent/<int:agent_id>/', views.agent_detail, name='pos-agent-detail'),
]
