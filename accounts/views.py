# accounts/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import* # Ensure you have an AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from events.models import Cart, Event

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.is_vendor:
                    return redirect('dashboard')  # Update with your URL name
                elif user.is_customer:
                    return redirect('customer_home')  # Update with your URL name
                elif user.is_posagent:
                    return redirect('pos_dashboard')  # Update with your URL name
                else:
                    messages.error(request, "You do not have access to any dashboards.")
                    return redirect('login')  # Redirect back to login if no access
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def universal_logout(request):
    logout(request)
    return redirect(reverse('universal_login')) 


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('all_events')  # Change this to your desired redirect after successful password change
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def add_to_cart(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, event=event)
    if created:
        cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    context = {'cart_items': cart_items}
    return render(request, 'events/view_cart.html', context)


@login_required
def delete_user_view(request):
    user = request.user  # Get the logged-in user

    if request.method == 'POST':
        # Store the user's email and username for the email
        user_email = user.email
        user_username = user.username

        # Delete the user
        user.delete()

        # Send account deletion confirmation email
        email_subject = 'Account Deletion Confirmation'
        email_body = (
            f"Dear {user_username},\n\n"
            "We're sorry to see you go. Your account has been successfully deleted.\n"
            "If you didn't request this deletion or if you have any concerns, "
            "please contact our support team immediately.\n\n"
            "Best regards,\n"
            "Your Company Team"
        )
        send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user_email])

        # Display a success message
        messages.success(request, "Your account has been deleted successfully.")
        
        # Redirect to a desired page after deletion
        return redirect(reverse_lazy('universal_login'))

    # Render the delete confirmation template
    return render(request, 'customers/delete_customer.html', {'user': user})