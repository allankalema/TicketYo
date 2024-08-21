from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TicketCategoryFormSet, TicketCategoryForm
from .models import *
from vendors.models import *

@login_required
def create_event(request):
    TicketCategoryFormSet = modelformset_factory(
        TicketCategory, form=TicketCategoryForm, extra=1, can_delete=True
    )
    
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
    # Retrieve all events and prefetch related ticket categories
    events = Event.objects.prefetch_related('ticket_categories').all()

    context = {
        'events': events
    }
    return render(request, 'events/all_events.html', context)

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, vendor=request.user)

    if request.method == 'POST':
        event.delete()
        return redirect('dashboard')  # Redirect to the vendor's dashboard after deletion

    return render(request, 'events/confirm_delete.html', {'event': event})