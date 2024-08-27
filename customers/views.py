import random
import string
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .forms import CustomerSignupForm, CustomerAuthenticationForm, CustomerUpdateForm, PasswordResetRequestForm, SetNewPasswordForm
from .models import Customer
from django.utils.encoding import force_str


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
        return render(request, 'customers/customer_email_verification.html', {'customer': customer})

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
            return render(request, 'customers/customer_email_verification.html', {'customer': customer})


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


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerUpdateForm
    template_name = 'customers/update_customer.html'
    success_url = reverse_lazy('customer_home')

    def get_object(self, queryset=None):
        return self.request.user  # Assuming the user is the customer

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)
    

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/delete_customer.html'
    success_url = reverse_lazy('customer_signup')

    def get_object(self, queryset=None):
        return self.request.user  # Assuming the logged-in user is the customer

    def delete(self, request, *args, **kwargs):
        # Get the customer's email before deletion
        customer_email = self.get_object().email
        customer_username = self.get_object().username
        
        # Perform the deletion
        response = super().delete(request, *args, **kwargs)

        # Send account deletion confirmation email
        email_subject = 'Account Deletion Confirmation'
        email_body = (
            f"Dear {customer_username},\n\n"
            "We're sorry to see you go. Your account has been successfully deleted.\n"
            "If you didn't request this deletion or if you have any concerns, "
            "please contact our support team immediately.\n\n"
            "Best regards,\n"
            "Your Company Team"
        )
        send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [customer_email])

        # Display a success message
        messages.success(request, "Your account has been deleted successfully.")
        
        return response
    

class CustomerPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'customers/change_password.html'
    success_url = reverse_lazy('customer_home')

    def form_valid(self, form):
        # Send an email notification to the user
        user = self.request.user
        email_subject = 'Password Changed Successfully'
        email_body = (
            f'Hi {user.first_name},\n\n'
            f'We wanted to let you know that your account password was changed successfully.\n'
            f'If you did not make this change, please contact our support team immediately.\n\n'
            f'Best regards,\n'
            f'Ticket yo'
        )
        send_mail(
            email_subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)

class PasswordResetRequestView(View):
    def get(self, request, *args, **kwargs):
        form = PasswordResetRequestForm()
        return render(request, 'customers/password_reset_request.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            customer = Customer.objects.get(email=email)
            verification_code = generate_verification_code()
            customer.verification_code = verification_code
            customer.verification_code_created_at = timezone.now()
            customer.save()

            # Send verification email
            email_subject = 'Your Password Reset Code'
            email_body = f'Your password reset code is {verification_code}.'
            send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [customer.email])

            return redirect('password_reset_verify', uidb64=urlsafe_base64_encode(force_bytes(customer.pk)))

        return render(request, 'customers/password_reset_request.html', {'form': form})


class PasswordResetVerifyView(View):
    def get(self, request, uidb64, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            customer = Customer.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
            customer = None

        if customer is not None:
            return render(request, 'customers/password_reset_verify.html', {'customer': customer})
        else:
            return redirect('password_reset_request')

    def post(self, request, uidb64, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            customer = Customer.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
            customer = None

        if customer is not None:
            code = request.POST.get('code')
            expiration_time = customer.verification_code_created_at + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                messages.error(request, "Verification code has expired.")
                return redirect('password_reset_request')

            if code == customer.verification_code:
                customer.verification_code = None  # Clear the code after verification
                customer.save()
                return redirect('password_reset_confirm', uidb64=uidb64)

            messages.error(request, "Invalid verification code.")
        else:
            messages.error(request, "Invalid request.")

        return render(request, 'customers/password_reset_verify.html', {'customer': customer})


class PasswordResetConfirmView(FormView):
    template_name = "customers/password_reset_confirm.html"
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('customer_home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        uidb64 = self.kwargs.get('uidb64')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            customer = Customer.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
            customer = None

        if customer is not None:
            kwargs['user'] = customer  # Pass the customer as the 'user' argument to the form
        return kwargs

    def form_valid(self, form):
        form.save()
        user = form.user
        login(self.request, user, backend='vendors.backends.VendorOrCustomerModelBackend')
        messages.success(self.request, "Your password has been reset successfully.")
        return super().form_valid(form)

    def dispatch(self, *args, **kwargs):
        uidb64 = self.kwargs.get('uidb64')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            self.customer = Customer.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
            self.customer = None

        if not self.customer:
            messages.error(self.request, "The reset link is invalid or has expired.")
            return redirect('password_reset_request')
        
        return super().dispatch(*args, **kwargs)
