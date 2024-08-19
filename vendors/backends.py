from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Vendor

class VendorOrUserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try authenticating as a Vendor
            vendor = Vendor.objects.get(username=username)
            if vendor.check_password(password):
                return vendor
        except Vendor.DoesNotExist:
            pass

        try:
            # Try authenticating as a User
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return Vendor.objects.get(pk=user_id)
        except Vendor.DoesNotExist:
            try:
                return UserModel.objects.get(pk=user_id)
            except UserModel.DoesNotExist:
                return None
