from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event
from django.db.models import Q
from datetime import datetime
from accounts.models import User
from events.models import *
import random
from django.http import HttpResponse
from vendors.decorators import vendor_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from pos.models import AgentEventAssignment
from .forms import *
from tickets.models import *
from django.http import JsonResponse
from tickets.views import prepare_event_data, get_user_entity, process_ticket_purchase


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

    # Retrieve "my agents" assigned to the current vendor
    my_agents = AgentEventAssignment.objects.filter(vendor=request.user).select_related('agent')

    # Ensure agents are unique and extract first and last names
    my_agents_unique = {assignment.agent.id: assignment.agent for assignment in my_agents}

    # Handle the search functionality for "My Agents"
    my_agents_search_query = request.GET.get('my_agents_search', '')
    if my_agents_search_query:
        my_agents_unique = {id: agent for id, agent in my_agents_unique.items() if
                            my_agents_search_query.lower() in agent.first_name.lower() or 
                            my_agents_search_query.lower() in agent.last_name.lower()}

    context = {
        'user': request.user,
        'available_agents_page': available_agents_page,
        'search_query': search_query,
        'my_agents': list(my_agents_unique.values()),  # Convert to a list for rendering
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


def agent_detail(request, agent_id):
    # Retrieve the agent using the provided agent_id
    agent = get_object_or_404(User, id=agent_id, is_posagent=True)

    context = {
        'agent': agent,
        # You can add more context if needed
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
    # Retrieve all event assignments for the currently logged-in POS agent
    assignments = AgentEventAssignment.objects.filter(agent=request.user)
    
    context = {
        'assignments': assignments
    }
    
    return render(request, 'pos/pos_dashboard.html', context) 


@user_passes_test(lambda u: u.is_authenticated and u.is_posagent)
def update_pos_agent_profile(request):
    # Fetch the currently logged-in user
    user = get_object_or_404(User, pk=request.user.pk, is_posagent=True)

    if request.method == 'POST':
        form = POSAgentProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('pos_dashboard')  # Redirect to POS dashboard after update
    else:
        form = POSAgentProfileForm(instance=user)

    return render(request, 'pos/update_agent.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.is_posagent)
def event_action_view(request, assignment_id):
    assignment = get_object_or_404(AgentEventAssignment, id=assignment_id)
    event = assignment.event
    vendor = assignment.vendor
    tickets = Ticket.objects.filter(event=event, user=vendor)

    context = {
        'assignment': assignment,
        'can_generate_tickets': assignment.generating_tickets,
        'can_verify_tickets': assignment.verifying_tickets,
        'verification_result': None,
        'error_message': None
    }

    if request.method == 'POST' and request.POST.get('ticket_number'):
        ticket_number = request.POST.get('ticket_number')
        ticket = tickets.filter(ticket_number__iexact=ticket_number).first()

        if ticket:
            if ticket.verified:
                context['error_message'] = 'This ticket has already been verified.'
            else:
                ticket.verified = True
                ticket.verified_by = request.user
                ticket.save()

                ticket_category_title = ticket.ticket_category.category_title if ticket.ticket_category else 'N/A'
                context['verification_result'] = {
                    'ticket_category': ticket_category_title,
                    'customer_username': ticket.customer_username or 'N/A',
                    'purchase_date': ticket.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                }
        else:
            context['error_message'] = 'Ticket not found.'

    return render(request, 'pos/event_action.html', context)


@login_required
def pos_generate_ticket_view(request, assignment_id):
    assignment = get_object_or_404(AgentEventAssignment, id=assignment_id)
    event = assignment.event
    vendor = assignment.vendor

    event_data, error = prepare_event_data(event.id)
    if error:
        return render(request, error['template'], error['context'])

    if request.method == 'POST':
        buyer = request.user
        buyer_type = 'pos_agent'

        purchase_data, error = process_ticket_purchase(
            event=event_data['event'], 
            ticket_data=event_data['ticket_data'], 
            ordinary_ticket_data=event_data['ordinary_ticket_data'], 
            tickets_info=request.POST, 
            buyer=buyer, 
            buyer_type=buyer_type
        )
        if error:
            return render(request, error['template'], error['context'])

        context = {
             'assignment': assignment,
             'assignment_id': assignment.id,
            'event': event_data['event'],
            'vendor': vendor,
            'ticket_details': purchase_data['ticket_details'],
            'total_price': purchase_data['total_price'],
            'total_tickets': purchase_data['total_tickets'],
            'customer': buyer,
            'ticket_data': event_data['ticket_data'],
            'ordinary_ticket_data': event_data['ordinary_ticket_data'],
        }
        return render(request, 'tickets/ticket_success.html', context)

    return render(request, 'tickets/buy_ticket.html', event_data)


@vendor_required
@login_required
def assign_events_to_pos_agent(request, agent_id):
    # Ensure agent exists and is a POS agent
    agent = get_object_or_404(User, id=agent_id, is_posagent=True)
    
    # Filter only the approved events for the current vendor (request.user)
    user_events = Event.objects.filter(
        user=request.user,
        start_date__gte=timezone.now(),
        status='approved'  # Filter for approved events
    ).order_by('start_date')

    if request.method == 'POST':
        # Get selected events and actions
        selected_events_ids = request.POST.getlist('events')
        generate_tickets = 'Generate Tickets' in request.POST.getlist('actions')
        verify_events = 'Verify Events' in request.POST.getlist('actions')

        if selected_events_ids:
            event_details = []
            
            # Loop through each selected event and assign permissions
            for event_id in selected_events_ids:
                event = get_object_or_404(Event, id=event_id)

                # Create or update an AgentEventAssignment record for this agent and event
                AgentEventAssignment.objects.update_or_create(
                    agent=agent,
                    event=event,
                    defaults={
                        'generating_tickets': generate_tickets,
                        'verifying_tickets': verify_events,
                        'vendor': request.user,  # The vendor who is assigning the event
                    }
                )

                # Collect event titles for the email notification
                event_details.append(event.title)

            # Prepare actions for email notification
            action_list = []
            if generate_tickets:
                action_list.append('Generate Tickets')
            if verify_events:
                action_list.append('Verify Events')
            action_list_str = ', '.join(action_list) if action_list else "No specific actions selected"

            # Send email to the POS agent with the assignment details
            try:
                send_mail(
                    'Event Assignment Notification',
                    f'Hello {agent.first_name},\n\nThis is from TicketYo. You have been assigned the following events by {request.user.first_name} {request.user.last_name} (Vendor):\n\n'
                    f'{", ".join(event_details)}\n\n'
                    f'Actions to carry out: {action_list_str}\n\n'
                    'Please ensure you handle these assignments responsibly.',
                    settings.DEFAULT_FROM_EMAIL,
                    [agent.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')

            # Display success message
            messages.success(request, f'Successfully assigned events to {agent.first_name}.')
            return redirect('manage_pos_agents')  # Redirect to the manage POS agents page

    return render(request, 'pos/assign_events.html', {
        'agent': agent,
        'user_events': user_events,
    })

@login_required
@login_required
def invite_pos_agent(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message', '')
        vendor_first_name = request.user.first_name
        vendor_last_name = request.user.last_name
        vendor_email = request.user.email

        if email:
            # Prepare email content
            email_subject = "Invitation to Join TicketYo as a POS Agent"
            email_body = (
                f"Hello,\n\n"
                f"You are being invited by {vendor_first_name} {vendor_last_name} to become a POS agent for handling cash transactions and ticket verification for their events at TicketYo.\n\n"
                "If you agree, please proceed to TicketYo and sign up as a POS agent. You will be able to manage assigned events and perform actions.\n\n"
                "Thank you.\n"
                "Yours sincerely,\n"
                "The Management\n\n"
                f"For any inquiries, please contact the vendor at {vendor_email}."
            )

            # Include additional message if provided
            if message:
                email_body += f"\n\nAdditional Message:\n{message}"

            # Send the email
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,  # Replace with your default email
                [email],
                fail_silently=False,
            )

            messages.success(request, "Invitation sent successfully!")
            return redirect('manage_pos_agents')  # Change to your desired redirect

        messages.error(request, "Please provide a valid email.")
    
    return render(request, 'pos/invite_pos_agent.html')

@login_required
@vendor_required
def pos_agent_events(request, agent_id):
    # Get the POS agent by ID
    pos_agent = get_object_or_404(User, id=agent_id, is_posagent=True)

    # Fetch events assigned to this POS agent for the logged-in vendor
    assigned_events = AgentEventAssignment.objects.filter(agent=pos_agent, vendor=request.user).select_related('event')

    context = {
        'pos_agent': pos_agent,
        'assigned_events': assigned_events,
    }
    return render(request, 'pos/pos_agent_events.html', context)


@login_required
@vendor_required
def pos_event_detail(request, event_id):
    # Get the event by ID
    event = get_object_or_404(Event, id=event_id)
    
    # Fetch the associated agent assignment for the current vendor
    agent_assignment = get_object_or_404(AgentEventAssignment, event=event, vendor=request.user)

    # Fetch ticket categories associated with the event
    ticket_categories = TicketCategory.objects.filter(event=event)

    # Calculate total tickets generated per category
    generated_totals = []
    total_generated = 0

    for category in ticket_categories:
        total_sold = category.category_tickets_sold
        price_per_ticket = category.category_price
        total_amount = total_sold * price_per_ticket
        total_generated += total_amount
        generated_totals.append({
            'title': category.category_title,
            'sold': total_sold,
            'price': price_per_ticket,
            'total': total_amount,
        })

    # Handle ordinary tickets if no categories exist
    if not ticket_categories.exists():
        total_sold = event.tickets_sold
        price_per_ticket = event.regular_price
        total_amount = total_sold * price_per_ticket
        generated_totals.append({
            'title': 'Ordinary',
            'sold': total_sold,
            'price': price_per_ticket,
            'total': total_amount,
        })

    # Check if verifying tickets is allowed
    verifying_enabled = agent_assignment.verifying_tickets
    verified_totals = []

    if verifying_enabled:
        # Placeholder logic for tracking verified tickets
        verified_data = {}  # Replace with actual logic to get verified tickets data
        for category in ticket_categories:
            # Fetch verified tickets based on category
            verified_count = verified_data.get(category.id, 0)  # Adjust as per your logic
            verified_totals.append({
                'title': category.category_title,
                'verified': verified_count,
            })

        # If no verified totals exist, add a default entry for ordinary tickets
        if not verified_totals:
            verified_totals.append({
                'title': 'Ordinary',
                'verified': 0,
            })

    # Total verified tickets count
    total_verified = sum(item['verified'] for item in verified_totals)

    context = {
        'event': event,
        'generated_totals': generated_totals,
        'total_generated': total_generated,
        'verifying_enabled': verifying_enabled,
        'verified_totals': verified_totals,
        'total_verified': total_verified,
    }
    return render(request, 'pos/pos_event_detail.html', context)


@login_required
@vendor_required
def deassign_event(request, event_id):
    # Get the event assignment and delete it
    assignment = get_object_or_404(AgentEventAssignment, event__id=event_id, vendor=request.user)
    assignment.delete()
    return redirect('pos-agent-events') 