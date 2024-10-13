from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,  PermissionsMixin
from vendors.models import Vendor
from events.models import Event

class POSAgentManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('POSAgents must have an email address')
        if not username:
            raise ValueError('POSAgents must have a username')
        if not first_name:
            raise ValueError('POSAgents must have a first name')
        if not last_name:
            raise ValueError('POSAgents must have a last name')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, email, password=None):
        raise NotImplementedError("Superuser creation is not supported for POSAgents.")

class POSAgent(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='pos_agents')
    assigned_events = models.ManyToManyField(Event, related_name='assigned_agents')
    is_active = models.BooleanField(default=True)
    is_posagent = models.BooleanField(default=True)

    objects = POSAgentManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
