from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EventForm, TicketCategoryFormSet
from .models import Event

@login_required
def create_event(request):
    # Remove the unnecessary check if we assume the request.user is already a Vendor.

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        formset = TicketCategoryFormSet(request.POST)

        if event_form.is_valid() and formset.is_valid():
            event = event_form.save(commit=False)
            event.vendor = request.user  # Directly assign the logged-in user as the vendor
            event.save()

            formset.instance = event
            formset.save()

            return redirect('dashboard')  # Redirect to vendor's dashboard

    else:
        event_form = EventForm()
        formset = TicketCategoryFormSet()

    context = {
        'event_form': event_form,
        'formset': formset
    }
    return render(request, 'events/create_event.html', context)
