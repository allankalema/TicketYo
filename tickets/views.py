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
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import EmailMessage


def prepare_event_data(event_id):
    event = get_object_or_404(Event, id=event_id)
    categories = event.ticket_categories.all()
    
    if event.is_sold_out():
        return None, {'template': 'tickets/sold_out.html', 'context': {'event': event}}
    
    ticket_data = [
        {'category': category, 
         'tickets_remaining': category.category_tickets_available - category.category_tickets_sold}
        for category in categories
    ]
    
    ordinary_ticket_data = None
    if not categories.exists():
        ordinary_remaining = event.tickets_available - event.tickets_sold
        ordinary_ticket_data = {'price': event.sale_price, 'tickets_remaining': ordinary_remaining}
    
    return {'event': event, 'ticket_data': ticket_data, 'ordinary_ticket_data': ordinary_ticket_data}, None

def get_user_entity(request):
    if hasattr(request.user, 'is_vendor') and request.user.is_vendor:
        return 'vendor', request.user
    elif hasattr(request.user, 'is_customer') and request.user.is_customer:
        return 'customer', request.user
    else:
        return None, None


def process_ticket_purchase(event, ticket_data, ordinary_ticket_data, tickets_info, entity, entity_type):
    ticket_details = []
    total_tickets = 0
    total_price = 0
    
    for data in ticket_data:
        category = data['category']
        quantity = int(tickets_info.get(f'quantity_{category.id}', 0))
        if quantity > 0:
            if category.is_category_sold_out() or category.category_tickets_sold + quantity > category.category_tickets_available:
                return None, {'template': 'events/sold_out.html', 'context': {'event': event}}
            ticket_details += generate_tickets(event, category, quantity, entity, entity_type)
            total_tickets += quantity
            total_price += quantity * category.category_price
            category.category_tickets_sold += quantity
            category.save()
    
    if not ticket_data and ordinary_ticket_data:
        quantity = int(tickets_info.get('quantity_ordinary', 0))
        if quantity > 0:
            if event.is_sold_out() or event.tickets_sold + quantity > event.tickets_available:
                return None, {'template': 'events/sold_out.html', 'context': {'event': event}}
            ticket_details += generate_tickets(event, None, quantity, entity, entity_type)
            total_tickets += quantity
            total_price += quantity * event.sale_price
    
    event.tickets_sold += total_tickets
    event.save()
    
    return {'ticket_details': ticket_details, 'total_tickets': total_tickets, 'total_price': total_price}, None


def generate_tickets(event, category, quantity, entity, entity_type):
    tickets = []
    for _ in range(quantity):
        ticket_number = Ticket.generate_ticket_number(event=event, vendor=event.vendor, category=category, entity=entity, entity_type=entity_type)
        qr_image = generate_qr_code(ticket_number)
        ticket = Ticket.objects.create(
            event=event,
            ticket_category=category,
            customer_username=entity.username,
            vendor=event.vendor,
            ticket_number=ticket_number,
            qr_code=qr_image,
            entity_type=entity_type
        )
        tickets.append({
            'ticket_number': ticket_number,
            'category': category.category_title if category else 'Ordinary',
            'price': category.category_price if category else event.sale_price,
            'qr_code_url': ticket.qr_code.url
        })
    return tickets

def generate_qr_code(ticket_number):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(ticket_number)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    return File(buffer, name=f'{ticket_number}_qr.png')


@login_required
def buy_ticket(request, event_id):
    event_data, error = prepare_event_data(event_id)
    if error:
        return render(request, error['template'], error['context'])
    
    if request.method == 'POST':

        msisdn = request.POST.get('msisdn')
        entity_type, entity = get_user_entity(request)
        if not entity:
            return render(request, 'tickets/error.html', {'message': 'User is not authorized to buy tickets.'})

        purchase_data, error = process_ticket_purchase(
            event_data['event'], event_data['ticket_data'], event_data['ordinary_ticket_data'], request.POST, entity, entity_type
        )
        if error:
            return render(request, error['template'], error['context'])
        
        context = {
            'event': event_data['event'],
            'vendor': event_data['event'].vendor,
            'ticket_details': purchase_data['ticket_details'],
            'total_price': purchase_data['total_price'],
            'total_tickets': purchase_data['total_tickets'],
            'customer': entity,
            'ticket_data': event_data['ticket_data'],
            'ordinary_ticket_data': event_data['ordinary_ticket_data'],
            'msisdn': msisdn
        }
        return render(request, 'tickets/ticket_success.html', context)

    return render(request, 'tickets/buy_ticket.html', event_data)



@login_required
def download_ticket_pdf(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    event = ticket.event  # Get the associated event
    vendor = event.vendor  # Get the associated vendor

    # Create absolute URLs for QR code and poster
    qr_code_url = request.build_absolute_uri(ticket.qr_code.url)
    poster_url = request.build_absolute_uri(event.poster.url)  # Ensure you use 'event.poster.url'

    context = {
        'ticket': ticket,
        'event': event,
        'vendor': vendor,
        'qr_code_url': qr_code_url,  # Add absolute URL for QR code
        'poster_url': poster_url,  # Add absolute URL for poster
    }

    template_path = 'tickets/ticket_pdf.html'
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{ticket.ticket_number}_ticket.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def send_ticket_receipts(request, ticket_details):
    email = EmailMessage(
        'Your Ticket Receipts',
        'Thank you for your purchase! Attached are your tickets.',
        'from@example.com',
        [request.user.email]
    )

    # Attach each ticket as a PDF
    for detail in ticket_details:
        pdf_content = generate_pdf_for_ticket(detail)  # Function to generate PDF
        email.attach(f"{detail['ticket_number']}_ticket.pdf", pdf_content, 'application/pdf')

    email.send()

def generate_pdf_for_ticket(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


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

                # Safely retrieve the category title
                ticket_category_title = 'N/A'
                if ticket.ticket_category:
                    ticket_category_title = ticket.ticket_category.category_title

                return JsonResponse({
                    'status': 'success',
                    'ticket_category': ticket_category_title,
                    'customer_username': ticket.customer_username or 'N/A',
                    'purchase_date': ticket.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
                })
        else:
            return JsonResponse({'status': 'error', 'message': 'Ticket not found.'})

    return render(request, 'tickets/verify_ticket.html', {'event': event})
