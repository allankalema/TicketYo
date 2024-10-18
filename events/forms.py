from django import forms
from django.forms import inlineformset_factory,HiddenInput
from .models import Event, TicketCategory, Cart

class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        required=False
    )

    class Meta:
        model = Event
        fields = [
            'poster', 'title', 'description', 'category',
            'start_date', 'end_date', 'venue_name', 'regular_price', 
            'sale_price', 'tickets_available'
        ]

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['category_title', 'category_price', 'category_tickets_available']

TicketCategoryFormSet = inlineformset_factory(
    Event, TicketCategory, form=TicketCategoryForm, extra=1, can_delete=True, widgets={'DELETE': HiddenInput()}
)



# class AddToCartForm(forms.ModelForm):
#     class Meta:
#         model = Cart
#         fields = []