from django.urls import path
from . import views

from .views import home
from .cart_views import cart_view, add_to_cart, remove_from_cart, update_cart
from .views import checkout_view, order_confirmation_view

urlpatterns = [
    path('', home, name='storefront_home'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', order_confirmation_view, name='order_confirmation'),
]
