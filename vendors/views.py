import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from accounts.models import User  # Change to User
from events.models import *
from django.conf import settings
from django.utils import timezone
from .forms import *
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages
from .decorators import vendor_required
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from tickets.models import Ticket
from events.models import Event
from django.db.models import Q

# Generate a 6-character verification code
def generate_verification_code():
    return get_random_string(length=6, allowed_chars=string.ascii_uppercase + string.digits)

def vendor_signup(request):
    if request.method == 'POST':
        form = VendorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_vendor = True  # Set vendor flag
            user.is_active = False  # Prevent login before verification
            
            # Assign the store name and store phone to the user model
            user.storename = form.cleaned_data['store_name']
            user.store_phone = form.cleaned_data['store_phone']  # Ensure this field is added to the User model if needed
            
            # Generate and save the verification code
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.save()

            # Send verification email
            email_subject = 'Your Verification Code'
            email_body = f'Your verification code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect('vendor_verify_email', pk=user.pk)
    else:
        form = VendorSignupForm()
    return render(request, 'vendors/vendor_signup.html', {'form': form})

def vendor_verify_email(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        
        # Check if the code has expired
        expiration_time = user.verification_code_created_at + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            messages.error(request, "Verification code has expired. Please sign up again.")
            return redirect('vendor_signup')
        
        # Validate the entered code
        if code == user.verification_code:
            user.is_active = True
            user.verification_code = None  # Clear the code after successful verification
            user.save()

            # Log in the vendor
            login(request, user)

            # Send a welcome email
            email_subject = 'Welcome to Ticket Yo'
            email_body = f'Hi {user.username}, welcome to Ticket Yo! You can now manage your store and events.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect('dashboard')  # Redirect to the vendor dashboard
        else:
            messages.error(request, "Invalid verification code. Please try again.")
    
    return render(request, 'vendors/verify_email.html', {'user': user})   


@login_required
@vendor_required
def vendor_dashboard(request):
    user = request.user  # Change to User
    events = Event.objects.filter(user=user, status='approved')  # Change to User

    # Handling search queries
    search_query = request.GET.get('search', '')
    
    if search_query:
        events = events.filter(Q(title__icontains=search_query))

    # Categorize events
    past_events = []
    upcoming_events = []
    sold_out_past_events = []
    sold_out_upcoming_events = []

    for event in events:
        remaining_tickets = event.tickets_available - event.tickets_sold
        
        if event.start_date < timezone.now():
            if remaining_tickets == 0:
                sold_out_past_events.append(event)
            else:
                past_events.append(event)
        else:
            if remaining_tickets == 0:
                sold_out_upcoming_events.append(event)
            else:
                upcoming_events.append(event)

    # Count pending events
    pending_events_count = Event.objects.filter(status='pending').count()

    # Total tickets sold and top 5 events by ticket sales
    tickets_sold_per_event = {}
    for event in events:
        tickets_sold_per_event[event] = Ticket.objects.filter(event=event).count()

    top_5_events = sorted(tickets_sold_per_event.items(), key=lambda x: x[1], reverse=True)[:5]
    total_tickets_sold = sum(tickets_sold_per_event.values())

    context = {
        'past_events': past_events,
        'upcoming_events': upcoming_events,
        'sold_out_past_events': sold_out_past_events,
        'sold_out_upcoming_events': sold_out_upcoming_events,
        'total_tickets_sold': total_tickets_sold,
        'top_5_events': top_5_events,
        'inventory': Ticket.objects.filter(customer_username=user.username, entity_type='vendor'),
        'search_query': search_query,
        'pending_count': pending_events_count,  # Add pending events count to context
    }

    return render(request, 'vendors/dashboard.html', context)

@login_required
@vendor_required
def view_inventory(request):
    user = request.user  # Change to User
    inventory = Ticket.objects.filter(customer_username=user.username, entity_type='vendor')

    return render(request, 'vendors/inventory.html', {'inventory': inventory})

@login_required 
def ticket_receipt(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'vendors/receipt.html', {'ticket': ticket})

@login_required
@vendor_required
def pending_events(request):
    # Retrieve and sort events with pending status by start date (closest first)
    pending_events_list = Event.objects.filter(status='pending').order_by('start_date')

    context = {
        'pending_events': pending_events_list,
    }

    return render(request, 'events/pending_events.html', context)

@login_required
@vendor_required
def events_confirmed_view(request):
    user = request.user  # Change to User

    # Get all action logs for the user, sorted by the latest action first
    action_logs = ActionLog.objects.filter(admin_user=user).select_related('event').order_by('-timestamp')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        search_query = search_query.lower()
        action_logs = action_logs.filter(
            Q(event__title__icontains=search_query) |
            Q(event__user__storename__icontains=search_query) |
            Q(event__status__icontains=search_query) |
            Q(event__venue_name__icontains=search_query) |
            Q(timestamp__icontains=search_query)
        )

    context = {
        'action_logs': action_logs,
        'search_query': search_query,
    }
    return render(request, 'events/events_confirmed.html', context)

def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)


@login_required
def update_vendor_profile(request):
    if not request.user.is_vendor:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('all_events')  # Or any other page you want to redirect to

    if request.method == 'POST':
        form = VendorProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('dashboard')  # Refresh the page to see updated data
    else:
        form = VendorProfileUpdateForm(instance=request.user)

    return render(request, 'vendors/update_vendor.html', {'form': form})