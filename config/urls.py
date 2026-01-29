from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('', include(tf_urls)),  # Make 2FA login the default
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('storefront.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('sellers/', include('sellers.urls')),
    path('payments/', include('payments.urls')),
    path('moderation/', include('moderation.urls')),
    path('reviews/', include('reviews.urls')),
    path('legal/', include('legal.urls')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
