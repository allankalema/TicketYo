from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class VendorManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, storename, store_phone, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            storename=storename,
            store_phone=store_phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, storename, store_phone, password=None):
        user = self.create_user(
            username,
            email,
            first_name,
            last_name,
            storename,
            store_phone,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class Vendor(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    storename = models.CharField(max_length=50)
    store_phone = models.CharField(max_length=15)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_created_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = VendorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'storename', 'store_phone']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
