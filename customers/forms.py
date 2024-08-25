# customers/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Customer

class CustomerSignupForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class CustomerAuthenticationForm(AuthenticationForm):
    pass
