from django.shortcuts import render, redirect, get_object_or_404
from events.models import Event, TicketCategory
from .models import Ticket
from django.contrib.auth.decorators import login_required

@login_required
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    categories = event.ticket_categories.all()

    # Calculate the 30% threshold for each category
    category_thresholds = {}
    for category in categories:
        category_thresholds[category.id] = category.category_tickets_available * 0.3

    if request.method == 'POST':
        tickets_info = request.POST  # Retrieve ticket quantities per category
        total_tickets = 0
        total_price = 0
        ticket_details = []

        for category in categories:
            quantity = int(tickets_info.get(f'quantity_{category.id}', 0))
            if quantity > 0:
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

        # Handling ordinary ticket
        if not categories.exists():
            quantity = int(tickets_info.get('quantity_ordinary', 0))
            if quantity > 0:
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

        # Pass detailed information to the template
        context = {
            'event': event,
            'vendor': event.vendor,
            'ticket_details': ticket_details,
            'total_price': total_price,
            'total_tickets': total_tickets,
            'customer': request.user,
        }

        return render(request, 'tickets/ticket_success.html', context)

    return render(request, 'tickets/buy_ticket.html', {
        'event': event,
        'categories': categories,
        'category_thresholds': category_thresholds
    })
