from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TicketCategoryFormSet, TicketCategoryForm, TicketCategoryFormSet
from .models import *
from vendors.models import *
from django.contrib import messages
from vendors.decorators import vendor_required
from datetime import timedelta
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse 
from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.forms import inlineformset_factory

@login_required
@vendor_required
def create_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        formset = TicketCategoryFormSet(request.POST, request.FILES, prefix='tickets')

        if event_form.is_valid() and formset.is_valid():
            # Save the event
            event = event_form.save(commit=False)
            event.vendor = request.user  # Assign the vendor to the event
            event.save()
            
            # Save the ticket categories
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    category = form.save(commit=False)
                    category.event = event
                    category.save()
            
            return redirect('dashboard')  # Redirect to the vendor's dashboard
    else:
        event_form = EventForm()
        formset = TicketCategoryFormSet(prefix='tickets')

    context = {
        'event_form': event_form,
        'formset': formset
    }
    return render(request, 'events/create_event.html', context)


@login_required
@vendor_required
def vendor_events(request):
    search_query = request.GET.get('search', '')  # Get search query
    filter_type = request.GET.get('filter', '')   # Get filter type ('upcoming' or 'past')

    # Base query for filtering based on the search query
    events = Event.objects.filter(
        Q(title__icontains=search_query) |
        Q(category__icontains=search_query) |
        Q(start_date__icontains=search_query) |
        Q(venue_name__icontains=search_query) |
        Q(regular_price__icontains=search_query) |
        Q(sale_price__icontains=search_query)
    ).filter(vendor=request.user)

    # Get current date
    current_date = timezone.now().date()

    # Filter based on upcoming or past events
    if filter_type == 'upcoming':
        events = events.filter(start_date__gte=current_date).order_by('start_date')
    elif filter_type == 'past':
        events = events.filter(start_date__lt=current_date).order_by('-start_date')

    # Calculate tickets remaining and attach it to each event
    for event in events:
        event.tickets_remaining = event.tickets_available - event.tickets_sold

    context = {
        'events': events,
        'filter_type': filter_type  # Pass the filter type to the template
    }
    return render(request, 'events/vendor_events.html', context)


def all_events(request):
    current_date = timezone.now()
    upcoming_threshold = current_date + timedelta(days=7)
    query = request.GET.get('q', '')

    events = Event.objects.prefetch_related('ticket_categories').filter(status='approved')

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(venue_name__icontains=query) |
            Q(vendor__first_name__icontains=query) |
            Q(vendor__storename__icontains=query)
        )

    upcoming_events = []
    sold_out_events = []

    # Filter events
    for event in events:
        tickets_available = event.tickets_available or 0
        tickets_sold = event.tickets_sold or 0
        event.remaining_tickets = tickets_available - tickets_sold

        for category in event.ticket_categories.all():
            category_tickets_available = category.category_tickets_available or 0
            category_tickets_sold = category.category_tickets_sold or 0
            category.remaining_tickets = category_tickets_available - category_tickets_sold
        
        # Condition for upcoming events
        if (event.start_date and event.start_date >= current_date) or (event.end_date and event.end_date >= current_date):
            # Move to sold-out category if tickets are sold out
            if event.remaining_tickets == 0:
                sold_out_events.append(event)
            else:
                upcoming_events.append(event)

    # Sort upcoming and sold-out events by the nearest date
    upcoming_events = sorted(upcoming_events, key=lambda e: e.start_date or e.end_date)
    sold_out_events = sorted(sold_out_events, key=lambda e: e.start_date or e.end_date)

    # Pagination for upcoming events (12 per page) and sold-out events (6 per page)
    upcoming_paginator = Paginator(upcoming_events, 12)
    sold_out_paginator = Paginator(sold_out_events, 6)

    page_number_upcoming = request.GET.get('upcoming_page')
    page_number_sold_out = request.GET.get('sold_out_page')

    page_obj_upcoming = upcoming_paginator.get_page(page_number_upcoming)
    page_obj_sold_out = sold_out_paginator.get_page(page_number_sold_out)

    # AJAX handling for search requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        events_data = {
            'upcoming_events': [
                {
                    'title': event.title,
                    'venue_name': event.venue_name,
                    'vendor_name': event.vendor.first_name,
                    'vendor_store': event.vendor.storename,
                    'remaining_tickets': event.remaining_tickets,
                    'poster_url': event.poster.url if event.poster else '',
                    'event_url': event.get_absolute_url(),
                }
                for event in upcoming_events
            ],
            'sold_out_events': [
                {
                    'title': event.title,
                    'venue_name': event.venue_name,
                    'vendor_name': event.vendor.first_name,
                    'vendor_store': event.vendor.storename,
                    'remaining_tickets': event.remaining_tickets,
                    'poster_url': event.poster.url if event.poster else '',
                    'event_url': event.get_absolute_url(),
                }
                for event in sold_out_events
            ]
        }
        return JsonResponse(events_data)

    context = {
        'page_obj_upcoming': page_obj_upcoming,
        'page_obj_sold_out': page_obj_sold_out,
        'query': query,
    }
    return render(request, 'events/all_events.html', context)


@login_required
@vendor_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, vendor=request.user)

    if request.method == 'POST':
        event.delete()
        return redirect('dashboard')  # Redirect to the vendor's dashboard after deletion

    return render(request, 'events/confirm_delete.html', {'event': event})


@login_required
@vendor_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        formset = TicketCategoryFormSet(request.POST, instance=event, prefix='tickets')

        if event_form.is_valid() and formset.is_valid():
            # Save the event
            event = event_form.save()

            # Save the ticket categories
            formset.instance = event  # Set the event instance to the formset
            formset.save()

            return redirect('dashboard')  # Redirect to the vendor's dashboard
    else:
        event_form = EventForm(instance=event)
        formset = TicketCategoryFormSet(instance=event, prefix='tickets')

    context = {
        'event_form': event_form,
        'formset': formset
    }
    return render(request, 'events/update_event.html', context)


@login_required
def add_to_cart(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
        # User is a Vendor
        cart_item, created = Cart.objects.get_or_create(
            vendor=request.user,  # Directly use request.user for the vendor
            event=event
        )
    elif hasattr(request.user, 'is_customer') and request.user.is_customer:
        # User is a Customer
        cart_item, created = Cart.objects.get_or_create(
            customer=request.user,  # Directly use request.user for the customer
            event=event
        )
    else:
        messages.error(request, 'You need to be logged in as a valid user.')
        return redirect('login')

    if created:
        messages.success(request, 'Event added to your cart.')
    else:
        messages.info(request, 'Event already in your cart.')

    return redirect('view_cart')

@login_required
def view_cart(request):
    if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
        # User is a Vendor
        cart_items = Cart.objects.filter(vendor=request.user)
    elif hasattr(request.user, 'is_customer') and request.user.is_customer:
        # User is a Customer
        cart_items = Cart.objects.filter(customer=request.user)
    else:
        messages.error(request, 'You need to be logged in as a valid user.')
        return redirect('login')

    return render(request, 'events/view_cart.html', {'cart_items': cart_items})


@login_required
def remove_from_cart(request, cart_item_id):
    # Fetch the cart item
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    # Ensure the user owns this cart item before deleting
    if (hasattr(request.user, 'is_vendor') and request.user.is_vendor and cart_item.vendor == request.user) or \
       (hasattr(request.user, 'is_customer') and request.user.is_customer and cart_item.customer == request.user):
        cart_item.delete()
        messages.success(request, 'Item removed from your cart.')
    else:
        messages.error(request, 'You do not have permission to remove this item.')

    return redirect('view_cart')



def event_detail(request, event_id):
    # Retrieve the event with prefetching related ticket categories
    event = Event.objects.prefetch_related('ticket_categories').get(id=event_id)

    # Calculate remaining tickets for the event
    tickets_available = event.tickets_available or 0
    tickets_sold = event.tickets_sold or 0
    event.remaining_tickets = tickets_available - tickets_sold

    # Calculate remaining tickets for each category
    for category in event.ticket_categories.all():
        category_tickets_available = category.category_tickets_available or 0
        category_tickets_sold = category.category_tickets_sold or 0
        category.remaining_tickets = category_tickets_available - category_tickets_sold

    # Check if the event has passed
    current_date = timezone.now()
    event.has_passed = False

    # If the event's end date is in the past or if the start date is in the past and there's no end date
    if (event.end_date and event.end_date < current_date) or (event.start_date and event.start_date < current_date and not event.end_date):
        event.has_passed = True

    context = {
        'event': event
    }
    return render(request, 'events/event_detail.html', context)


@login_required
@vendor_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id, status='approved')
    # Calculate tickets remaining
    event.tickets_remaining = event.tickets_available - event.tickets_sold
    
    context = {
        'event': event
    }
    return render(request, 'events/personal_event.html', context)


def past_events_view(request):
    current_date = timezone.now()
    query = request.GET.get('q', '')

    # Filter events based on the past event criteria and search query
    past_events = Event.objects.filter(
        (Q(end_date__lte=current_date) | Q(start_date__lte=current_date, end_date__isnull=True)),
        status='approved'
    ).filter(
        Q(title__icontains=query) | Q(venue_name__icontains=query) | Q(vendor__storename__icontains=query)
    ).order_by('-start_date') # Sort by recently completed

    # Pagination: 12 events per page
    paginator = Paginator(past_events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'past_events': page_obj,
        'query': query,  # To retain the search term in the search box
        'page_obj': page_obj  # For pagination
    }
    return render(request, 'events/past_events.html', context)

@vendor_required
@login_required
def approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.status == 'pending':
        event.status = 'approved'
        event.adminaction = request.user  # Automatically set the admin user who approved
        event.save()
        messages.success(request, f"Event '{event.title}' has been approved.")
    else:
        messages.warning(request, f"Event '{event.title}' is already {event.status}.")
    
    return redirect(reverse('admin:events_event_changelist'))  # Update: Dynamically resolves the event change list in admin

@vendor_required
@login_required
def reject_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.status == 'pending':
        event.status = 'rejected'
        event.adminaction = request.user  # Automatically set the admin user who rejected
        event.save()
        messages.success(request, f"Event '{event.title}' has been rejected.")
    else:
        messages.warning(request, f"Event '{event.title}' is already {event.status}.")
    
    return redirect(reverse('admin:events_event_changelist'))  # Update: Dynamically resolves the event change list in admin



@login_required
@vendor_required
def dash_approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Create the form and formset for editing the event and its ticket categories
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)
        ticket_formset = TicketCategoryFormSet(request.POST, instance=event)

        if event_form.is_valid() and ticket_formset.is_valid():
            event_form.save()
            ticket_formset.save()

            # Get the selected status from the form
            status = request.POST.get('status')
            # Update event status and log admin action
            event.status = status
            event.adminaction = request.user  # Set the admin who made the action

            # Log the action
            ActionLog.objects.create(admin_user=request.user, event=event, action=status)

            # Prepare email details
            subject = f"Your Event '{event.title}' Status Update"
            message = f"Your event has been {status}. Please contact management for further information."
            recipient_list = [event.vendor.email]  # Assuming the vendor has an email field

            # Send email notification
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

            # Save the event and show success message
            event.save()
            messages.success(request, 'Event status updated, and the vendor has been notified.')
            return redirect('pending_events')  # Redirect to the pending events page
    else:
        event_form = EventForm(instance=event)
        ticket_formset = TicketCategoryFormSet(instance=event)

    context = {
        'event': event,
        'event_form': event_form,
        'ticket_formset': ticket_formset,
    }
    return render(request, 'events/approve_event.html', context)
