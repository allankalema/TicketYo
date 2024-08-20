from django import forms
from .models import Event, TicketCategory

class EventForm(forms.ModelForm):
    manage_inventory = forms.BooleanField(required=False, label='Manage Inventory')

    class Meta:
        model = Event
        fields = [
            'poster', 'title', 'description', 'category', 'start_date',
            'end_date', 'venue_name', 'regular_price', 'sale_price'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['end_date'].required = False
        self.fields['sale_price'].required = False

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['category_title', 'category_price', 'category_tickets_available']

    def __init__(self, *args, **kwargs):
        super(TicketCategoryForm, self).__init__(*args, **kwargs)
        # Default title for the first ticket category
        self.fields['category_title'].initial = 'Ordinary'
        self.fields['category_price'].initial = kwargs.get('initial').get('sale_price') if kwargs.get('initial') else None

# Formset for Ticket Categories
TicketCategoryFormSet = forms.inlineformset_factory(
    Event, TicketCategory, form=TicketCategoryForm, extra=1, can_delete=True
)
