from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('movies/', include('movies.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('halls/', include('halls.urls')),
    path('sessions/', include('cinema_sessions.urls')),
    path('tickets/', include('tickets.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
