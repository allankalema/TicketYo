from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomerSignupForm, CustomerAuthenticationForm

class CustomerSignupView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerSignupForm()
        return render(request, 'customers/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('customer_home')
        return render(request, 'customers/signup.html', {'form': form})

class CustomerLoginView(View):
    def get(self, request, *args, **kwargs):
        form = CustomerAuthenticationForm()
        return render(request, 'customers/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomerAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('customer_home')
        return render(request, 'customers/login.html', {'form': form})

@login_required
def customer_home(request):
    return render(request, 'customers/customer_home.html')

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('customer_login')
