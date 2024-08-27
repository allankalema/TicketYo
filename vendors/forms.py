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

class VendorUpdateForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['username', 'email', 'first_name', 'last_name', 'storename', 'store_phone']

class VendorPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Vendor.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no vendor registered with this email address.")
        return email

class VendorSetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="New password")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data