import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Vendor
from events.models import *
from django.conf import settings
from django.utils import timezone
from .forms import *
from .backends import VendorOrCustomerModelBackend 
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

def generate_verification_code():
    return get_random_string(length=6, allowed_chars=string.ascii_uppercase + string.digits)

def signup(request):
    if request.method == 'POST':
        form = VendorCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate verification code and store it with the user
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.is_active = False  # Prevent login before verification
            user.save()
            
            # Send verification email
            verification_link = request.build_absolute_uri(
                reverse('verify_email', args=[user.pk])
            )
            email_subject = 'Your Verification Code'
            email_body = f'Your verification code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect('verify_email', pk=user.pk)
    else:
        form = VendorCreationForm()

    return render(request, 'vendors/signup.html', {'form': form})


def verify_email(request, pk):
    user = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        attempts = request.session.get('attempts', 0)
        
        # Check if code has expired
        expiration_time = user.verification_code_created_at + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            user.delete()
            return redirect('signup')
        
        if code == user.verification_code:
            # Code is correct, activate the user
            user.is_active = True
            user.verification_code = None  # Clear the code after verification
            user.save()
            
            # Log in the user
            login(request, user, backend='vendors.backends.VendorOrCustomerModelBackend')
            
            # Send a welcome email
            email_subject = 'Welcome to Ticket Yo'
            email_body = f'Hi {user.username}, welcome to Ticket Yo!'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            return redirect('dashboard')
        else:
            attempts += 1
            request.session['attempts'] = attempts
            if attempts >= 5:
                user.delete()  # Discard the user data after 5 failed attempts
                return redirect('signup')
            else:
                error_message = 'Invalid code. Please try again.'
                return render(request, 'vendors/verify_email.html', {'error': error_message})
    else:
        return render(request, 'vendors/verify_email.html')
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password, is_vendor_login=True)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "You are not a vendor! Please sign in as your appropriate category.")
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'vendors/login.html', {'form': form})

@login_required
@vendor_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@vendor_required
def vendor_dashboard(request):
    vendor = request.user
    events = Event.objects.filter(vendor=vendor, status='approved')

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
        'inventory': Ticket.objects.filter(customer_username=vendor.username, entity_type='vendor'),
        'search_query': search_query,
        'pending_count': pending_events_count,  # Add pending events count to context
    }

    return render(request, 'vendors/dashboard.html', context)

@login_required
@vendor_required
def update_vendor(request):
    vendor = get_object_or_404(Vendor, pk=request.user.pk)
    if request.method == 'POST':
        form = VendorUpdateForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VendorUpdateForm(instance=vendor)
    return render(request, 'vendors/update_vendor.html', {'form': form})


@login_required
@vendor_required
def delete_vendor(request):
    vendor = get_object_or_404(Vendor, username=request.user.username)
    if request.method == 'POST':
        vendor_email = vendor.email  # Store the vendor's email before deletion
        vendor.delete()
        logout(request)

        # Send account deletion confirmation email
        email_subject = 'Account Deletion Confirmation'
        email_body = (
            f"Dear {vendor.username},\n\n"
            "We're sorry to see you go. Your account has been successfully deleted.\n"
            "If you didn't request this deletion or if you have any concerns, "
            "please contact our support team immediately.\n\n"
            "Best regards,\n"
            "TicketYo"
        )
        
        print("About to send email to:", vendor_email)
        try:
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [vendor_email])
            print("Email sent successfully")
        except Exception as e:
            print("Error sending email:", str(e))

        return redirect('login')
    return render(request, 'vendors/delete_vendor.html', {'vendor': vendor})

@login_required
@vendor_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session
            
            # Send an email notification
            email_subject = 'Your Ticket Yo Password has been Changed'
            email_body = (
                f'Hi {user.username},\n\n'
                f'This is to inform you that your password was changed successfully. If you did not initiate this change, please contact our support team immediately.\n\n'
                f'Thank you,\n'
                f'The Ticket Yo Team'
            )
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            
            messages.success(request, "Your password has been changed successfully.")
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'vendors/change_password.html', {'form': form})


def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)

def vendor_password_reset_request(request):
    if request.method == "POST":
        form = VendorPasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            vendor = Vendor.objects.get(email=email)
            verification_code = generate_verification_code()  # Function to generate a code
            vendor.verification_code = verification_code
            vendor.verification_code_created_at = timezone.now()
            vendor.save()

            # Send verification email
            email_subject = 'Your Password Reset Code'
            email_body = f'Your password reset code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [vendor.email])

            return redirect('vendor_password_reset_verify', uidb64=urlsafe_base64_encode(force_bytes(vendor.pk)))
    else:
        form = VendorPasswordResetRequestForm()

    return render(request, 'vendors/password_reset_request.html', {'form': form})



def vendor_password_reset_verify(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        vendor = Vendor.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Vendor.DoesNotExist):
        vendor = None

    if vendor is not None:
        if request.method == "POST":
            code = request.POST.get('code')
            expiration_time = vendor.verification_code_created_at + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                messages.error(request, "Verification code has expired.")
                return redirect('vendor_password_reset_request')

            if code == vendor.verification_code:
                vendor.verification_code = None  # Clear the code after verification
                vendor.save()
                return redirect('vendor_password_reset_confirm', uidb64=uidb64)

            messages.error(request, "Invalid verification code.")
        return render(request, 'vendors/password_reset_verify.html', {'vendor': vendor})
    else:
        messages.error(request, "Invalid request.")
        return redirect('vendor_password_reset_request')

def vendor_password_reset_confirm(request, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        vendor = Vendor.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Vendor.DoesNotExist):
        vendor = None

    if vendor is not None:
        if request.method == "POST":
            form = VendorSetNewPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password1']
                vendor.set_password(new_password)
                vendor.save()

                # Log the vendor in automatically
                login(request, vendor, backend='vendors.backends.VendorOrCustomerModelBackend')

                # Send confirmation email
                email_subject = 'Password Changed Successfully'
                email_body = 'Your password has been changed successfully. If you did not perform this action, please contact support immediately.'
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [vendor.email])

                messages.success(request, "Your password has been reset successfully.")
                return redirect('dashboard')  # Redirect to the vendor dashboard after login
        else:
            form = VendorSetNewPasswordForm()

        return render(request, 'vendors/password_reset_confirm.html', {'form': form, 'vendor': vendor})
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect('vendor_password_reset_request')

@login_required    
def view_inventory(request):
    vendor = request.user
    inventory = Ticket.objects.filter(customer_username=vendor.username, entity_type='vendor')

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
    admin_user = request.user

    # Get all action logs for the logged-in admin, sorted by the latest action first
    action_logs = ActionLog.objects.filter(admin_user=admin_user).select_related('event').order_by('-timestamp')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        search_query = search_query.lower()
        action_logs = [log for log in action_logs if 
                       search_query in log.event.title.lower() or
                       search_query in log.event.vendor.storename.lower() or
                       search_query in log.event.status.lower() or
                       search_query in log.event.venue_name.lower() or
                       search_query in str(log.event.start_date)]

    context = {
        'action_logs': action_logs,
        'search_query': search_query,
    }
    return render(request, 'events/events_confirmed.html', context)
