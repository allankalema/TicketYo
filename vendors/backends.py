from django.contrib.auth.backends import ModelBackend
from vendors.models import Vendor
from customers.models import Customer
from pos.models import POSAgent  # Import the POSAgent model

class VendorOrCustomerModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        is_vendor_login = kwargs.get('is_vendor_login', False)
        is_posagent_login = kwargs.get('is_posagent_login', False)
        
        try:
            if is_vendor_login:
                # Authenticate as a vendor
                vendor = Vendor.objects.get(username=username)
                if vendor.check_password(password) and vendor.is_vendor:
                    return vendor
                   

            elif is_posagent_login:
                pos_agent = POSAgent.objects.get(username=username)
                if pos_agent.check_password(password) and pos_agent.is_posagent:
                        return pos_agent
            else:
                # Authenticate as a customer
                customer = Customer.objects.get(username=username)
                if customer.check_password(password) and customer.is_customer:
                    return customer
        except (Vendor.DoesNotExist, Customer.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return Vendor.objects.get(pk=user_id)
        except Vendor.DoesNotExist:
            try:
                return Customer.objects.get(pk=user_id)
            except Customer.DoesNotExist:
                try:
                    return POSAgent.objects.get(pk=user_id)  # Get POS Agent here
                except POSAgent.DoesNotExist:
                    return None