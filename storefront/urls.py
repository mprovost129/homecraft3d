from django.urls import path
app_name = 'storefront'
from .views.views import home, checkout_view, order_confirmation_view
from .views.settings import storefront_settings_view
from .cart_views import cart_view, add_to_cart, remove_from_cart, update_cart, empty_cart

urlpatterns = [
    path('', home, name='storefront_home'),
    path('settings/', storefront_settings_view, name='storefront_settings'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('cart/empty/', empty_cart, name='empty_cart'),
    path('order-confirmation/<int:order_id>/', order_confirmation_view, name='order_confirmation'),
]
