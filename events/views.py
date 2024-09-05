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
    if isinstance(request.user, Vendor):
        events = Event.objects.filter(vendor=request.user)  # Retrieve all events by the logged-in vendor
    else:
        return redirect('login')

    context = {
        'events': events
    }
    return render(request, 'events/vendor_events.html', context)


def all_events(request):
    events = Event.objects.prefetch_related('ticket_categories').all()
    upcoming_threshold = timezone.now() + timedelta(days=7)
    query = request.GET.get('q', '')
    
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(venue_name__icontains=query) |
            Q(vendor__first_name__icontains=query) |
            Q(vendor__storename__icontains=query)
        )

    upcoming_events = []
    other_events = []

    for event in events:
        tickets_available = event.tickets_available or 0
        tickets_sold = event.tickets_sold or 0
        event.remaining_tickets = tickets_available - tickets_sold

        for category in event.ticket_categories.all():
            category_tickets_available = category.category_tickets_available or 0
            category_tickets_sold = category.category_tickets_sold or 0
            category.remaining_tickets = category_tickets_available - category_tickets_sold
        
        if event.start_date <= upcoming_threshold:
            upcoming_events.append(event)
        else:
            other_events.append(event)

    # Use headers to check for an AJAX request
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
            'other_events': [
                {
                    'title': event.title,
                    'venue_name': event.venue_name,
                    'vendor_name': event.vendor.first_name,
                    'vendor_store': event.vendor.storename,
                    'remaining_tickets': event.remaining_tickets,
                    'poster_url': event.poster.url if event.poster else '',
                    'event_url': event.get_absolute_url(),
                }
                for event in other_events
            ]
        }
        return JsonResponse(events_data)

    context = {
        'upcoming_events': upcoming_events,
        'other_events': other_events,
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


@login_required
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

    context = {
        'event': event
    }
    return render(request, 'events/event_detail.html', context)
