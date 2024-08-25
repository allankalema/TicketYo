# customers/backends.py
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

# Set up logging
logger = logging.getLogger(__name__)

class CustomerBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            logger.error(f"Authentication failed: User with username '{username}' does not exist.")
            return None

        if not user.check_password(password):
            logger.error(f"Authentication failed: Incorrect password for user '{username}'.")
            return None

        logger.info(f"Authentication successful for user '{username}'.")
        return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            logger.error(f"User with ID '{user_id}' does not exist.")
            return None
