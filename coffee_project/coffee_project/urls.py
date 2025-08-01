from django.contrib import admin
from django.urls import path, include

# For serving media files during development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),         # Admin panel URL
    path('', include('shop.urls')),          # App URLs from 'shop' app
]

# Media file handling (for product images, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
