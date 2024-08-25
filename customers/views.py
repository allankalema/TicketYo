# customers/views.py
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from .forms import CustomerSignupForm, CustomerAuthenticationForm
from vendors.backends import *

class CustomerSignupView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerSignupForm()
        return render(request, 'customers/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            customer = form.save()
            login(request, customer, backend='vendors.backends.VendorOrCustomerModelBackend')
            return redirect('customer_home')
        return render(request, 'customers/signup.html', {'form': form})

class CustomerLoginView(LoginView):
    template_name = 'customers/login.html'
    authentication_form = CustomerAuthenticationForm

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user, backend='vendors.backends.VendorOrCustomerModelBackend')
            return redirect('customer_home')
        return self.form_invalid(form)


class CustomerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'customers/customer_home.html'

class CustomerLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('customer_login')
