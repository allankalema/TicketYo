from django import forms
from django.forms import inlineformset_factory
from .models import Event, TicketCategory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'poster', 'title', 'description', 'category', 'start_date',
            'end_date', 'venue_name', 'regular_price', 'sale_price',
            'tickets_available'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['sale_price'].required = False
        self.fields['tickets_available'].required = False

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['category_title', 'category_price', 'category_tickets_available']

# Formset for Ticket Categories
TicketCategoryFormSet = inlineformset_factory(
    Event, TicketCategory, form=TicketCategoryForm, extra=1, can_delete=True
)
