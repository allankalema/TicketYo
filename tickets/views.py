from django.shortcuts import render, redirect, get_object_or_404
from events.models import Event, TicketCategory
from .models import Ticket
from django.contrib.auth.decorators import login_required

@login_required
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    categories = event.ticket_categories.all()

    # Check if the event is sold out
    if event.is_sold_out():
        return render(request, 'tickets/sold_out.html', {'event': event})

    # Initialize variables to store ticket data
    ticket_data = []
    ordinary_ticket_data = None

    # Calculate remaining tickets for each category
    for category in categories:
        remaining_tickets = category.category_tickets_available - category.category_tickets_sold
        ticket_data.append({
            'category': category,
            'tickets_remaining': remaining_tickets
        })

    # Handle ordinary tickets if no categories are available
    if not categories.exists():
        ordinary_remaining = event.tickets_available - event.tickets_sold
        ordinary_ticket_data = {
            'price': event.sale_price,
            'tickets_remaining': ordinary_remaining
        }

    if request.method == 'POST':
        tickets_info = request.POST
        total_tickets = 0
        total_price = 0
        ticket_details = []

        for data in ticket_data:
            category = data['category']
            quantity = int(tickets_info.get(f'quantity_{category.id}', 0))
            if quantity > 0:
                if category.is_category_sold_out() or category.category_tickets_sold + quantity > category.category_tickets_available:
                    return render(request, 'events/sold_out.html', {'event': event})

                for _ in range(quantity):
                    ticket_number = Ticket.generate_ticket_number(
                        event=event,
                        vendor=event.vendor,
                        category=category,
                        customer=request.user
                    )
                    Ticket.objects.create(
                        event=event,
                        ticket_category=category,
                        customer=request.user,
                        vendor=event.vendor,
                        ticket_number=ticket_number
                    )
                    ticket_details.append({
                        'ticket_number': ticket_number,
                        'category': category.category_title,
                        'price': category.category_price,
                    })
                total_tickets += quantity
                total_price += quantity * category.category_price

                category.category_tickets_sold += quantity
                category.save()

        if not categories.exists() and ordinary_ticket_data:
            quantity = int(tickets_info.get('quantity_ordinary', 0))
            if quantity > 0:
                if event.is_sold_out() or event.tickets_sold + quantity > event.tickets_available:
                    return render(request, 'events/sold_out.html', {'event': event})

                for _ in range(quantity):
                    ticket_number = Ticket.generate_ticket_number(
                        event=event,
                        vendor=event.vendor,
                        category=None,
                        customer=request.user
                    )
                    Ticket.objects.create(
                        event=event,
                        ticket_category=None,
                        customer=request.user,
                        vendor=event.vendor,
                        ticket_number=ticket_number
                    )
                    ticket_details.append({
                        'ticket_number': ticket_number,
                        'category': 'Ordinary',
                        'price': event.sale_price,
                    })
                total_tickets += quantity
                total_price += quantity * event.sale_price

        event.tickets_sold += total_tickets
        event.save()

        context = {
            'event': event,
            'vendor': event.vendor,
            'ticket_details': ticket_details,
            'total_price': total_price,
            'total_tickets': total_tickets,
            'customer': request.user,
            'ticket_data': ticket_data,
            'ordinary_ticket_data': ordinary_ticket_data
        }

        return render(request, 'tickets/ticket_success.html', context)

    context = {
        'event': event,
        'ticket_data': ticket_data,
        'ordinary_ticket_data': ordinary_ticket_data
    }
    return render(request, 'tickets/buy_ticket.html', context)
