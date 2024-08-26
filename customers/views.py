# customers/views.py
import random
import string
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from .forms import CustomerSignupForm, CustomerAuthenticationForm
from vendors.backends import *
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class CustomerSignupView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerSignupForm()
        return render(request, 'customers/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            # Generate and save verification code
            verification_code = generate_verification_code()
            customer.verification_code = verification_code
            customer.verification_code_created_at = timezone.now()
            customer.is_active = False  # Prevent login before verification
            customer.save()

            # Send verification email
            email_subject = 'Your Verification Code'
            email_body = f'Your verification code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [customer.email])

            return redirect('customer_verify_email', pk=customer.pk)
        return render(request, 'customers/signup.html', {'form': form})

class CustomerVerifyEmailView(View):
    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=pk)
        return render(request, 'customers/customer_email_verfication.html', {'customer': customer})

    def post(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=pk)
        code = request.POST.get('code')

        # Check if the code is correct and not expired
        expiration_time = customer.verification_code_created_at + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            messages.error(request, "Verification code has expired.")
            return redirect('signup')

        if code == customer.verification_code:
            customer.is_verified = True
            customer.is_active = True
            customer.verification_code = None  # Clear the code after verification
            customer.save()

            # Log in the customer
            login(request, customer, backend='vendors.backends.VendorOrCustomerModelBackend')

            # Send welcome email
            email_subject = 'Welcome to Our Platform'
            email_body = f'Hi {customer.username}, welcome to Our Platform!'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [customer.email])

            return redirect('customer_home')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, 'customers/verify_email.html', {'customer': customer})


class CustomerLoginView(LoginView):
    template_name = 'customers/login.html'
    authentication_form = CustomerAuthenticationForm

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None and hasattr(user, 'is_customer') and user.is_customer:
            login(self.request, user, backend='vendors.backends.VendorOrCustomerModelBackend')
            return redirect('customer_home')
        else:
            messages.error(self.request, "Invalid credentials or account type.")
        return self.form_invalid(form)


class CustomerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'customers/customer_home.html'

class CustomerLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('customer_login')
