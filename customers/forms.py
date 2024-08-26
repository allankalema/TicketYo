# customers/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,  UserChangeForm, PasswordChangeForm
from .models import Customer

class CustomerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = Customer
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomerAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerUpdateForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = ['username', 'email', 'first_name', 'last_name']

class CustomerPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = Customer