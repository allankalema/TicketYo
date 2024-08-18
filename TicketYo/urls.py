from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('vendors/', include('vendors.urls')),
    path('admin-panel/', include('admin_panel.urls')),  # Renamed to avoid conflict with 'admin/' path
    path('', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/', include('api.urls')),
]
