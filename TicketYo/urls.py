from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from vendors.views import custom_permission_denied_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('vendors/', include('vendors.urls')),
    path('events', include('events.urls')),
    path('tickets/', include('tickets.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('analytics/', include('analytics.urls')),
    path('', include('frontend.urls')),
    path('api/', include('api.urls')),
    path('pos/', include('pos.urls')),
    path('Accounts/', include('accounts.urls')),
     path('accounts/', include('allauth.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = custom_permission_denied_view
