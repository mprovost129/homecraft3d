from django.urls import path
from django.views.generic import RedirectView
from .views.dashboard import dashboard
from .views.products import manage_products, edit_product, delete_product, remove_media, duplicate_product, seller_product_analytics
from .views import orders

urlpatterns = [
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),
    path('dashboard/', dashboard, name='dashboard'),
    path('products/', manage_products, name='manage_products'),
    path('products/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('products/<int:product_id>/media/<int:media_id>/remove/', remove_media, name='remove_media'),
    path('products/<int:product_id>/duplicate/', duplicate_product, name='duplicate_product'),
    path('analytics/', seller_product_analytics, name='product_analytics'),
]
