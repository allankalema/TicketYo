# # middleware.py
# from django.utils.deprecation import MiddlewareMixin
# from vendors.models import Vendor  # Adjust imports as needed
# from accounts.models import User # Import your models
# from customers.models import Customer
# from pos.models import POSAgent

# class UserInstanceMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         if request.user.is_authenticated:
#             user_type = request.session.get('user_type')

#             if user_type == 'vendor':
#                 request.user_instance = Vendor.objects.get(user=request.user)
#             elif user_type == 'customer':
#                 request.user_instance = Customer.objects.get(user=request.user)
#             elif user_type == 'pos_agent':
#                 request.user_instance = POSAgent.objects.get(user=request.user)
#             else:
#                 request.user_instance = None
#         else:
#             request.user_instance = None
