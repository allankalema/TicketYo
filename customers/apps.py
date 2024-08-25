# customers/apps.py
from django.apps import AppConfig

class CustomersConfig(AppConfig):
    name = 'customers'
    verbose_name = 'Customers'

    def ready(self):
        # import customers.signals  # Comment this out if no signals exist
        pass
