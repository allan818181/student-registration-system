"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('academics/', include('apps.academics.urls', namespace='academics')),
    path('enrollment/', include('apps.enrollment.urls', namespace='enrollment')),
    path('reports/', include('apps.reporting.urls', namespace='reporting')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
