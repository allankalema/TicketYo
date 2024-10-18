import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

from .forms import UserSignupForm, UpdateCustomerForm
from accounts.models import User
from tickets.models import Ticket

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def user_signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate and save verification code
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.is_active = False  # Prevent login before verification
            user.save()

            # Send verification email
            email_subject = 'Your Verification Code'
            email_body = f'Your verification code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect('user_verify_email', pk=user.pk)
    else:
        form = UserSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def user_verify_email(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        code = request.POST.get('code')

        # Check if the code is correct and not expired
        expiration_time = user.verification_code_created_at + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            messages.error(request, "Verification code has expired.")
            return redirect('signup')

        if code == user.verification_code:
            user.is_verified = True
            user.is_active = True
            user.verification_code = None  # Clear the code after verification
            user.save()

            # Log in the user
            login(request, user)

            # Send welcome email
            email_subject = 'Welcome to Our Platform'
            email_body = f'Hi {user.username}, welcome to Our Platform!'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])

            return redirect('customer_home')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
    return render(request, 'accounts/user_email_verification.html', {'user': user})

@login_required
def user_home(request):
    user = request.user
    # Get all tickets for the logged-in user
    tickets = Ticket.objects.filter(user=user)  # Use user foreign key instead of customer_username
    # Get distinct events from those tickets
    events = {ticket.event for ticket in tickets}
    
    return render(request, 'customers/customer_home.html', {
        'events': events,
        'tickets': tickets,
    })

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def update_customer(request):
    user = request.user  # Get the logged-in user

    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # Save the updated user information
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('customer_home')  # Redirect to the desired page after successful update
    else:
        form = UpdateCustomerForm(instance=user)  # Prepopulate the form with the user's current info

    return render(request, 'customers/update_customer.html', {'form': form})
