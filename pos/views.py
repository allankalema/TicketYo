from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event
from django.db.models import Q
from datetime import datetime
from accounts.models import User
import random
from vendors.decorators import vendor_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator


@login_required
@vendor_required
def manage_pos_agents(request):
    if not request.user.is_vendor:
        return redirect('all_events')

    # Get the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Retrieve all available POS agents
    available_agents = User.objects.filter(is_posagent=True)

    # Filter by search query if it exists
    if search_query:
        available_agents = available_agents.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(username__icontains=search_query)
        ).distinct()

    # Pagination for available agents (5 per page)
    paginator = Paginator(available_agents, 5)
    page_number = request.GET.get('page')
    available_agents_page = paginator.get_page(page_number)

    # Retrieve "my agents" (implementation for determining 'my agents' will come later)
    my_agents = []  # Placeholder for now, modify this later

    context = {
        'user': request.user,
        'available_agents_page': available_agents_page,
        'search_query': search_query,
        'my_agents': my_agents,  # This will be filled later
    }

    return render(request, 'pos/manage_agents.html', context)


@login_required
def create_pos_agent(request):
    if not request.user.is_vendor:
        return redirect('home')

    events = request.user.events.filter(
        Q(status='approved') & 
        (Q(start_date__gte=datetime.now()) | Q(end_date__gte=datetime.now()))
    )

    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        selected_event_ids = request.POST.getlist('events')

        # Create and save the POS agent
        agent = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            vendor=request.user,
        )
        
        # Assign selected events to the POS agent
        selected_events = Event.objects.filter(id__in=selected_event_ids)
        agent.assigned_events.set(selected_events)
        
        # Send email to the agent with credentials
        event_titles = ', '.join([event.title for event in selected_events])
        send_mail(
            'POS Agent Credentials',
            f'Hello {first_name},\n\nYou have been selected as a POS Agent for {request.user.storename}.' 
            f'\n\nThe following events have been assigned to you: {event_titles}.' 
            f'\n\nYour credentials are:\n\nemail: {email}' 
            '\n\n Please login to access your dashboard.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return redirect('manage_pos_agents')

    return render(request, 'pos/create_agent.html', {
        'events': events,
        'user': request.user,
    })


def verify_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            agent = User.objects.get(email=email)
            return redirect('signup_pos_agent', email=email)
        except User.DoesNotExist:
            messages.error(request, "You are not invited to become a POS Agent. Please contact the vendor.")
            return redirect('verify_email')

    return render(request, 'pos/verify_email.html')


def signup_pos_agent(request, email):
    try:
        agent = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "Invalid email. Please verify your email again.")
        return redirect('verify_email')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup_pos_agent', email=email)

        agent.first_name = first_name
        agent.last_name = last_name
        agent.username = username
        agent.password = make_password(password)
        agent.save()

        send_mail(
            'POS Agent Registration Complete',
            f'Hello {first_name},\n\nYou have successfully registered as a POS Agent.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        send_mail(
            'POS Agent Registered',
            f'The POS Agent {first_name} {last_name} has successfully registered.',
            settings.DEFAULT_FROM_EMAIL,
            [agent.vendor.email],
            fail_silently=False,
        )

        messages.success(request, "You have successfully registered as a POS Agent.")
        return redirect('all_events')

    return render(request, 'pos/signup_agent.html', {
        'first_name': agent.first_name,
        'last_name': agent.last_name,
        'email': agent.email,
        'assigned_events': agent.assigned_events.all(),
    })


@login_required
def agent_detail(request, agent_id):
    agent = User.objects.get(id=agent_id)
    total_tickets_sold = 0
    total_tickets_verified = 0
    total_amount_made = 0.00

    search_query = request.GET.get('search_events', '')
    assigned_events = agent.assigned_events.all()

    if search_query:
        assigned_events = assigned_events.filter(title__icontains=search_query)

    if not request.user.is_vendor:
        return redirect('home')

    all_events = request.user.events.filter(
        (Q(start_date__gte=timezone.now()) | Q(end_date__gte=timezone.now())),
        status='approved'
    )

    if request.method == 'POST':
        selected_event_ids = request.POST.getlist('events')
        if not selected_event_ids:
            messages.error(request, "At least one event must be allocated to the agent.")
        else:
            selected_events = Event.objects.filter(id__in=selected_event_ids)
            agent.assigned_events.set(selected_events)
            messages.success(request, "Events have been successfully updated.")
            return redirect('agent_detail', agent_id=agent.id)

    context = {
        'agent': agent,
        'assigned_events': assigned_events,
        'search_query': search_query,
        'total_tickets_sold': total_tickets_sold,
        'total_tickets_verified': total_tickets_verified,
        'total_amount_made': total_amount_made,
        'all_events': all_events,
    }
    
    return render(request, 'pos/agent_detail.html', context)


@login_required
def agent_action(request, agent_id):
    agent = User.objects.get(id=agent_id)

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

    return redirect('agent_detail', agent_id=agent.id)


@login_required
def pos_event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    tickets_created = []
    tickets_verified = []
    event_categories = event.ticket_categories.all()
    total_amount = 0

    for category in event_categories:
        category.total_amount = category.category_tickets_sold * category.category_price
        total_amount += category.total_amount

    context = {
        'event': event,
        'tickets_created': tickets_created,
        'tickets_verified': tickets_verified,
        'event_categories': event_categories,
        'total_amount': total_amount,
    }
    
    return render(request, 'pos/event_detail.html', context)


@user_passes_test(lambda u: u.is_authenticated and u.is_posagent)
def pos_dashboard(request):
    return render(request, 'pos/pos_dashboard.html')
