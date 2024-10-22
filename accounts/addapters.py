from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from events.models import Cart

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(MySocialAccountAdapter, self).save_user(request, sociallogin, form)
        
        # Automatically set is_customer to True for newly registered users
        user.is_customer = True
        user.save()

        return user
