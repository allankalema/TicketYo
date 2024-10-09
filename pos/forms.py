# pos/forms.py
from django import forms
from .models import POSAgent
from events.models import Event
from django.utils import timezone

class POSAgentForm(forms.ModelForm):
    assigned_events = forms.ModelMultipleChoiceField(
        queryset=Event.objects.filter(status='approved', start_date__gte=timezone.now()),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = POSAgent
        fields = ['first_name', 'last_name', 'email', 'assigned_events']
