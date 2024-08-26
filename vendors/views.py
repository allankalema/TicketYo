import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Vendor
from django.conf import settings
from django.utils import timezone
from .forms import *
from .backends import VendorOrCustomerModelBackend 
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib import messages

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
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'vendors/dashboard.html')

@login_required
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
def delete_vendor(request):
    vendor = get_object_or_404(Vendor, username=request.user.username)
    if request.method == 'POST':
        vendor.delete()
        logout(request)
        return redirect('login')
    return render(request, 'vendors/delete_vendor.html', {'vendor': vendor})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to update the session
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'vendors/change_password.html', {'form': form})