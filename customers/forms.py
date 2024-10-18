# customers/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,  UserChangeForm, PasswordChangeForm,SetPasswordForm 
# from .models import Customer
from accounts.models import User

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True  # Set the customer flag to True
        if commit:
            user.save()
        return user


class UpdateCustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }



