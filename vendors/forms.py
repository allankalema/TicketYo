from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Vendor

class VendorCreationForm(UserCreationForm):
    class Meta:
        model = Vendor
        fields = ['username', 'email', 'first_name', 'last_name', 'storename', 'store_phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
