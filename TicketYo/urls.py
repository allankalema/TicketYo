from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('vendors/', include('vendors.urls')),
    path('', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/', include('api.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
