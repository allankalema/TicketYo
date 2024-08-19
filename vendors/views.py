from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Vendor
from .forms import *

def signup(request):
    if request.method == 'POST':
        form = VendorCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = VendorCreationForm()
    return render(request, 'vendors/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'vendors/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    return render(request, 'vendors/dashboard.html')

@login_required
def update_vendor(request):
    vendor = get_object_or_404(Vendor, username=request.user.username)
    if request.method == 'POST':
        form = VendorCreationForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VendorCreationForm(instance=vendor)
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