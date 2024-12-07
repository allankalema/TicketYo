from django.urls import path
from . import views

urlpatterns = [
    path('manage_agents/', views.manage_pos_agents, name='manage_pos_agents'),
    path('agent_action/<int:agent_id>/', views.agent_action, name='agent_action'), 
    path('pos/dashboard/', views.pos_dashboard, name='pos_dashboard'), 

    path('inventory/', views.inventory_view, name='pos_inventory'),
    path('update-profile/', views.update_pos_agent_profile, name='update_pos_agent_profile'),
    path('invite-pos-agent/', views.invite_pos_agent, name='invite_pos_agent'),
    path('agent/<int:agent_id>/', views.agent_detail, name='pos-agent-detail'),
    path('assign-events/<int:agent_id>/', views.assign_events_to_pos_agent, name='assign_events_to_pos_agent'),
    path('pos-agent/<int:agent_id>/events/', views.pos_agent_events, name='pos-agent-events'),
    path('agent/<int:agent_id>/event/<int:event_id>/', views.pos_event_detail, name='pos_event_detail'),  # Use this pattern for pos_event_detail

    path('event/deassign/<int:event_id>/', views.deassign_event, name='deassign_event'),
    path('event-action/<int:assignment_id>/', views.event_action_view, name='event_action'),
    path('generate-ticket/<int:assignment_id>/', views.pos_generate_ticket_view, name='Generate_ticket'),
    path('signup/', views.pos_agent_signup, name='pos_signup'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
]
