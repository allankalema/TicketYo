from django.contrib.auth.backends import ModelBackend
from .models import Customer

class CustomerModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            customer = Customer.objects.get(username=username)
            if customer.check_password(password):
                return customer
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
