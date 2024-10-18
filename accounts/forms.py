# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from events.models import Cart

class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=30,
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Old Password"), widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("New Password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Confirm New Password"), widget=forms.PasswordInput)

    class Meta:
        model = None  # Not required as we are using the PasswordChangeForm directly
        fields = ('old_password', 'new_password1', 'new_password2')

class AddToCartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['event']