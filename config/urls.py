"""
Root URL configuration for AI Home Service Platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Web views
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('providers/', include('apps.providers.urls')),
    path('services/', include('apps.services.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('ai/', include('apps.ai_assistant.urls')),

    # REST API
    path('api/', include([
        path('auth/', include('apps.accounts.api_urls')),
        path('providers/', include('apps.providers.api_urls')),
        path('services/', include('apps.services.api_urls')),
        path('reviews/', include('apps.reviews.api_urls')),
        path('ai/', include('apps.ai_assistant.api_urls')),
        path('recommendations/', include('apps.recommendations.api_urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
