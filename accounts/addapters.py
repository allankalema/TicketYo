from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from events.models import Cart

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(MySocialAccountAdapter, self).save_user(request, sociallogin, form)
        
        # Create a cart for the user after the user is saved
        Cart.objects.create(user=user)
        
        return user
