from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TicketCategoryFormSet
from .models import Event, ActionLog
from django.contrib import messages
from vendors.decorators import vendor_required
from datetime import timedelta
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse 
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

@login_required
@vendor_required
def create_event(request):
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        formset = TicketCategoryFormSet(request.POST, request.FILES, prefix='tickets')

        if event_form.is_valid() and formset.is_valid():
            event = event_form.save(commit=False)
            event.user = request.user
            event.save()
            
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    category = form.save(commit=False)
                    category.event = event
                    category.save()
            
            return redirect('dashboard')
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
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', '')
    current_date = timezone.now().date()

    events = Event.objects.filter(
        Q(title__icontains=search_query) |
        Q(category__icontains=search_query) |
        Q(start_date__icontains=search_query) |
        Q(venue_name__icontains=search_query) |
        Q(regular_price__icontains=search_query) |
        Q(sale_price__icontains=search_query)
    ).filter(user=request.user)

    if filter_type == 'upcoming':
        events = events.filter(start_date__gte=current_date).order_by('start_date')
    elif filter_type == 'past':
        events = events.filter(start_date__lt=current_date).order_by('-start_date')

    for event in events:
        event.tickets_remaining = event.tickets_available - event.tickets_sold

    context = {
        'events': events,
        'filter_type': filter_type
    }
    return render(request, 'events/vendor_events.html', context)


def all_events(request):
    current_date = timezone.now()
    query = request.GET.get('q', '')

    # Fetching only approved events
    events = Event.objects.prefetch_related('ticket_categories').filter(status='approved')

    # Apply search filter only on approved events
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(venue_name__icontains=query) |
            Q(description__icontains=query)  # Search in description too
        )

    upcoming_events = []
    sold_out_events = []

    for event in events:
        event.remaining_tickets = event.tickets_available - event.tickets_sold

        for category in event.ticket_categories.all():
            category.remaining_tickets = category.category_tickets_available - category.category_tickets_sold

        if (event.start_date and event.start_date >= current_date) or (event.end_date and event.end_date >= current_date):
            if event.remaining_tickets == 0:
                sold_out_events.append(event)
            else:
                upcoming_events.append(event)

    upcoming_events = sorted(upcoming_events, key=lambda e: e.start_date or e.end_date)
    sold_out_events = sorted(sold_out_events, key=lambda e: e.start_date or e.end_date)

    upcoming_paginator = Paginator(upcoming_events, 12)
    sold_out_paginator = Paginator(sold_out_events, 6)

    page_number_upcoming = request.GET.get('upcoming_page')
    page_number_sold_out = request.GET.get('sold_out_page')

    page_obj_upcoming = upcoming_paginator.get_page(page_number_upcoming)
    page_obj_sold_out = sold_out_paginator.get_page(page_number_sold_out)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        events_data = [
            {
                'title': event.title,
                'venue_name': event.venue_name,
                'remaining_tickets': event.remaining_tickets,
                'poster_url': event.poster.url if event.poster else '',
                'event_url': event.get_absolute_url(),
            }
            for event in events
        ]
        return JsonResponse({'events': events_data})

    context = {
        'page_obj_upcoming': page_obj_upcoming,
        'page_obj_sold_out': page_obj_sold_out,
        'query': query,
    }
    return render(request, 'events/all_events.html', context)

@login_required
@vendor_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, user=request.user)

    if request.method == 'POST':
        event.delete()
        return redirect('dashboard')

    return render(request, 'events/confirm_delete.html', {'event': event})


@login_required
@vendor_required
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        formset = TicketCategoryFormSet(request.POST, instance=event, prefix='tickets')

        if event_form.is_valid() and formset.is_valid():
            event = event_form.save()
            formset.instance = event
            formset.save()

            return redirect('dashboard')
    else:
        event_form = EventForm(instance=event)
        formset = TicketCategoryFormSet(instance=event, prefix='tickets')

    context = {
        'event_form': event_form,
        'formset': formset
    }
    return render(request, 'events/update_event.html', context)


def event_detail(request, event_id):
    event = Event.objects.prefetch_related('ticket_categories').get(id=event_id)
    event.remaining_tickets = event.tickets_available - event.tickets_sold

    for category in event.ticket_categories.all():
        category.remaining_tickets = category.category_tickets_available - category.category_tickets_sold

    current_date = timezone.now()
    event.has_passed = False

    if (event.end_date and event.end_date < current_date) or (event.start_date and event.start_date < current_date and not event.end_date):
        event.has_passed = True

    context = {
        'event': event
    }
    return render(request, 'events/event_detail.html', context)


@login_required
@vendor_required
def dash_approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)
        ticket_formset = TicketCategoryFormSet(request.POST, instance=event)

        if event_form.is_valid() and ticket_formset.is_valid():
            event_form.save()
            ticket_formset.save()

            status = request.POST.get('status')
            event.status = status
            event.adminaction = request.user

            ActionLog.objects.create(admin_user=request.user, event=event, action=status)

            subject = f"Your Event '{event.title}' Status Update"
            message = f"Your event has been {status}. Please contact management for further information."
            recipient_list = [event.user.email]

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            event.save()

            messages.success(request, 'Event status updated, and the vendor has been notified.')
            return redirect('pending_events')
    else:
        event_form = EventForm(instance=event)
        ticket_formset = TicketCategoryFormSet(instance=event)

    context = {
        'event': event,
        'event_form': event_form,
        'ticket_formset': ticket_formset,
    }
    return render(request, 'events/approve_event.html', context)


def homepage(request):
    all_events = Event.objects.filter(status='approved')
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')

    paginator = Paginator(upcoming_events, 4)
    page_number = request.GET.get('upcoming_page')
    page_obj_upcoming = paginator.get_page(page_number)

    return render(request, 'events/homepage.html', {
        'all_events': all_events,
        'page_obj_upcoming': page_obj_upcoming,
    })


def past_events_view(request):
    current_date = timezone.now()
    query = request.GET.get('q', '')

    # Filter events based on the past event criteria and search query
    past_events = Event.objects.filter(
        (Q(end_date__lte=current_date) | Q(start_date__lte=current_date, end_date__isnull=True))
    ).filter(
        Q(title__icontains=query) | Q(venue_name__icontains=query) | Q(user__storename__icontains=query)
    ).order_by('-start_date')  # Sort by recently completed

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

@login_required
@vendor_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Calculate tickets remaining
    event.tickets_remaining = event.tickets_available - event.tickets_sold
    
    context = {
        'event': event
    }
    return render(request, 'events/personal_event.html', context)
