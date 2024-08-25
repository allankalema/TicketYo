# customers/views.py
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .models import Customer
from django.contrib.auth import login
from .forms import CustomerSignupForm, CustomerAuthenticationForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CustomerLoginView(LoginView):
    template_name = 'customers/login.html'
    authentication_form = CustomerAuthenticationForm

class CustomerSignupView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerSignupForm()
        return render(request, 'customers/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            customer = form.save()
            login(request, customer, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('customer_home')
        return render(request, 'customers/signup.html', {'form': form})
    
class CustomerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'customers/customer_home.html'
