# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from events.models import *

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


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is not registered. Please sign up.")
        return email

class CodeVerificationForm(forms.Form):
    code = forms.CharField(label="Enter the code sent to your email", max_length=6)

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)