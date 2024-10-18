# vendors/forms.py
from django import forms
from accounts.models import User

class VendorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'storename', 'store_phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'storename': forms.TextInput(attrs={'class': 'form-control'}),
            'store_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
