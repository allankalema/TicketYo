from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from vendors.models import Vendor
from customers.models import Customer  # Import the Customer model

class VendorOrCustomerModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try authenticating as a Vendor
            vendor = Vendor.objects.get(username=username)
            if vendor.check_password(password):
                return vendor
        except Vendor.DoesNotExist:
            pass

        try:
            # Try authenticating as a Customer
            customer = Customer.objects.get(username=username)
            if customer.check_password(password):
                return customer
        except Customer.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        try:
            return Vendor.objects.get(pk=user_id)
        except Vendor.DoesNotExist:
            try:
                return Customer.objects.get(pk=user_id)  # Fetch customer by primary key
            except Customer.DoesNotExist:
                return None
