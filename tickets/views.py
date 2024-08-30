from django.shortcuts import render, redirect, get_object_or_404
from events.models import Event, TicketCategory
from .models import Ticket
from django.contrib.auth.decorators import login_required
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from vendors.decorators import *
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta


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

        # Determine if the logged-in user is a Customer or Vendor
        if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
            entity_type = 'vendor'
            entity = request.user
            
        elif hasattr(request.user, 'is_customer') and request.user.is_customer:
            entity_type = 'customer'
            entity = request.user
        else:
            # Handle cases where the user is neither a Customer nor a Vendor
            return render(request, 'tickets/error.html', {'message': 'User is not authorized to buy tickets.'})

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
                                    entity=entity,  # Pass the determined entity here
                                    entity_type=entity_type  # Pass the determined entity type here
                                )

                    # Create a QR code for the ticket number
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(ticket_number)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer)
                    qr_image = File(buffer, name=f'{ticket_number}_qr.png')

                    # Create the ticket based on the entity type
                    if entity_type == 'customer':
                        ticket = Ticket.objects.create(
                            event=event,
                            ticket_category=category,
                            customer_username=entity.username,  # Assign entity as customer
                            vendor=event.vendor,
                            ticket_number=ticket_number,
                            qr_code=qr_image,  # assuming you have a `qr_code` field in your Ticket model
                            entity_type='customer'
                        )
                    elif entity_type == 'vendor':
                        ticket = Ticket.objects.create(
                            event=event,
                            ticket_category=category,
                            customer_username=entity.username,  
                            vendor=event.vendor,  # Assign entity as vendor
                            ticket_number=ticket_number,
                            qr_code=qr_image,  # assuming you have a `qr_code` field in your Ticket model
                            entity_type='vendor'
                        )

                    ticket_details.append({
                        'ticket_number': ticket_number,
                        'category': category.category_title,
                        'price': category.category_price,
                        'qr_code_url': ticket.qr_code.url  # Add the QR code URL to the ticket details
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
                        entity=entity,  # Pass the determined entity here
                        entity_type=entity_type  # Pass the determined entity type here
                    )

                    # Create a QR code for the ticket number
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(ticket_number)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer)
                    qr_image = File(buffer, name=f'{ticket_number}_qr.png')

                    # Create the ticket based on the entity type
                    if entity_type == 'customer':
                        ticket = Ticket.objects.create(
                            event=event,
                            ticket_category=None,
                            customer_username=entity.username,  # Assign entity as customer
                            vendor=event.vendor,
                            ticket_number=ticket_number,
                            qr_code=qr_image,  # assuming you have a `qr_code` field in your Ticket model
                            entity_type='customer'
                        )
                    elif entity_type == 'vendor':
                        ticket = Ticket.objects.create(
                            event=event,
                            ticket_category=None,
                            customer_username=entity.username,  
                            vendor=event.vendor,  
                            ticket_number=ticket_number,
                            qr_code=qr_image,  # assuming you have a `qr_code` field in your Ticket model
                            entity_type='vendor'
                        )

                    ticket_details.append({
                        'ticket_number': ticket_number,
                        'category': 'Ordinary',
                        'price': event.sale_price,
                        'qr_code_url': ticket.qr_code.url  # Add the QR code URL to the ticket details
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
            'customer': entity,
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



@login_required
def view_qr_codes(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event, customer=request.user)

    # Prepare a list of ticket details including QR code URLs
    ticket_details = []
    for ticket in tickets:
        ticket_details.append({
            'ticket_number': ticket.ticket_number,
            'category': ticket.ticket_category.category_title if ticket.ticket_category else 'Ordinary',
            'price': ticket.ticket_category.category_price if ticket.ticket_category else event.sale_price,
            'qr_code_url': ticket.qr_code.url if ticket.qr_code else None
        })

    context = {
        'event': event,
        'ticket_details': ticket_details
    }
    return render(request, 'tickets/view_qr_codes.html', context)

@login_required
@vendor_required
def verifiable_events(request):
    current_date = now().date()  # Get the current date
    vendor = request.user  # Assuming this gets the correct vendor associated with the user
    
    verifiable_events = Event.objects.filter(vendor=vendor)  # Filter events for the logged-in vendor
    events_data = []

    for event in verifiable_events:
        start_date = event.start_date.date()  # Truncate start_date to date only
        end_date = event.end_date.date() if event.end_date else None  # Handle cases with no end_date

        is_clickable = False
        should_display = False

        if start_date == current_date:
            # The event starts today, make it clickable and display it
            is_clickable = True
            should_display = True
        elif start_date < current_date:
            # The event has started in the past
            if end_date is None:
                # No end date, check if it has been less than 24 hours since start_date
                if now() <= event.start_date + timedelta(days=1):
                    # It's still within the 24-hour window
                    is_clickable = True
                    should_display = True
            else:
                # Event has an end date
                if start_date <= current_date <= end_date:
                    # Current date is between the start and end date, make it clickable and display it
                    is_clickable = True
                    should_display = True
                elif current_date == end_date + timedelta(hours=1):
                    # 1 hour after the end date, remove it from the list
                    should_display = False
                elif current_date > end_date:
                    # After the end date, don't display the event
                    should_display = False
        else:
            # Event's start_date is in the future
            should_display = True  # Display the event
            # The event is not clickable yet
            is_clickable = False

        if should_display:
            events_data.append({
                'event': event,
                'is_clickable': is_clickable,
            })

    context = {
        'verifiable_events': events_data,
    }
    return render(request, 'tickets/verifiable_events.html', context)


@login_required
@vendor_required
def verify_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    vendor = request.user
    
    # Ensure the correct tickets are being filtered by event and vendor
    tickets = Ticket.objects.filter(event=event, vendor=vendor)
    
    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number', '').strip()
        
        # Case-insensitive search and check if the ticket exists
        ticket = tickets.filter(ticket_number__iexact=ticket_number).first()
        
        if ticket:
            if ticket.verified:
                return JsonResponse({'status': 'error', 'message': 'This ticket has already been verified.'})
            else:
                # Mark the ticket as verified
                ticket.verified = True
                ticket.save()
                return JsonResponse({
                    'status': 'success',
                    'ticket_category': ticket.ticket_category.name if ticket.ticket_category else 'N/A',
                    'customer_username': ticket.customer_username or 'N/A',
                    'purchase_date': ticket.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
        else:
            return JsonResponse({'status': 'error', 'message': 'Ticket not found.'})

    return render(request, 'tickets/verify_ticket.html', {'event': event})
