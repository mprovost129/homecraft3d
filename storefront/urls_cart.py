from django.urls import path
from .cart_views import add_to_cart, remove_from_cart, update_cart, cart_view

urlpatterns = [
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
]
