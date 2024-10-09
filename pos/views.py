from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from vendors.models import Vendor
from django.core.mail import send_mail
from django.conf import settings
from .models import POSAgent
from events.models import Event
from django.db.models import Q
from datetime import datetime
import random
from django.contrib import messages

@login_required
def manage_pos_agents(request):
    vendor = Vendor.objects.get(username=request.user.username)

    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Retrieve active and inactive agents associated with the vendor
    active_agents = vendor.pos_agents.filter(is_active=True)
    inactive_agents = vendor.pos_agents.filter(is_active=False)

    # If a search query exists, filter the agents accordingly
    if search_query:
        active_agents = active_agents.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(username__icontains=search_query) | 
            Q(assigned_events__title__icontains=search_query)
        ).distinct()

        inactive_agents = inactive_agents.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(username__icontains=search_query) | 
            Q(assigned_events__title__icontains=search_query)
        ).distinct()

    context = {
        'vendor': vendor,
        'active_agents': active_agents,
        'inactive_agents': inactive_agents,
        'search_query': search_query,
    }

    return render(request, 'pos/manage_agents.html', context)


@login_required
def create_pos_agent(request):
    vendor = Vendor.objects.get(username=request.user.username)
    events = vendor.events.filter(
        Q(status='approved') & 
        (Q(start_date__gte=datetime.now()) | Q(end_date__gte=datetime.now()))
    )

    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        selected_event_ids = request.POST.getlist('events')

        # Create a 6-digit random password
        password = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Create a unique username based on email
        username = email.split('@')[0]

        # Create and save the POS agent
        agent = POSAgent.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            vendor=vendor,
            password=password,  # Save the generated password
        )
        
        # Assign selected events to the POS agent
        selected_events = Event.objects.filter(id__in=selected_event_ids)
        agent.assigned_events.set(selected_events)
        
        # Send email to the agent with credentials
        event_titles = ', '.join([event.title for event in selected_events])
        send_mail(
            'POS Agent Credentials',
            f'Hello {first_name},\n\nYou have been selected as a POS Agent for the vendor {vendor.storename}.' 
            f'\n\nThe following events have been assigned to you: {event_titles}.' 
            f'\n\nYour credentials are:\nUsername: {username}\nPassword: {password}\n' 
            'Please login to access your dashboard.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Redirect to manage_agents or success page
        return redirect('manage_pos_agents')

    # If it's a GET request, render the form
    return render(request, 'pos/create_agent.html', {
        'events': events,
        'vendor': vendor,
    })

@login_required
def agent_detail(request, agent_id):
    agent = POSAgent.objects.get(id=agent_id)
    
    # Example placeholders for statistics (you can replace these with actual logic)
    total_tickets_sold = 0  # Replace with actual logic to calculate total tickets sold
    total_tickets_verified = 0  # Replace with actual logic
    total_amount_made = 0.00  # Replace with actual logic

    # Get the search query for events
    search_query = request.GET.get('search_events', '')

    # Filter assigned events if a search query is provided
    assigned_events = agent.assigned_events.all()
    if search_query:
        assigned_events = assigned_events.filter(title__icontains=search_query)

    context = {
        'agent': agent,
        'assigned_events': assigned_events,
        'search_query': search_query,
        'total_tickets_sold': total_tickets_sold,
        'total_tickets_verified': total_tickets_verified,
        'total_amount_made': total_amount_made,
    }
    
    return render(request, 'pos/agent_detail.html', context)


@login_required
def agent_action(request, agent_id):
    agent = POSAgent.objects.get(id=agent_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'deactivate':
            agent.is_active = False
            agent.save()
            messages.success(request, f"{agent.first_name} has been deactivated.")
            return redirect('manage_pos_agents')

        elif action == 'delete':
            agent.delete()
            messages.success(request, f"{agent.first_name} has been deleted.")
            return redirect('manage_pos_agents')

    # In case of GET request or other issues, redirect to agent detail
    return redirect('agent_detail', agent_id=agent.id)


@login_required
def pos_event_detail(request, event_id):
    # Retrieve the event based on the ID
    event = Event.objects.get(id=event_id)

    # Get tickets created and verified (Placeholder logic, replace with actual logic)
    tickets_created = []  # Should eventually contain tickets created by the agent
    tickets_verified = []  # Should eventually contain tickets verified for this event

    # Get the ticket categories related to the event
    event_categories = event.ticket_categories.all()  # Get all ticket categories for this event

    # Calculate total tickets sold and the total amount for each category
    total_amount = 0
    for category in event_categories:
        category.total_amount = category.category_tickets_sold * category.category_price  # Calculate total amount for each category
        total_amount += category.total_amount  # Accumulate total amount for the event

    context = {
        'event': event,
        'tickets_created': tickets_created,
        'tickets_verified': tickets_verified,
        'event_categories': event_categories,
        'total_amount': total_amount,
    }
    
    return render(request, 'pos/event_detail.html', context)
