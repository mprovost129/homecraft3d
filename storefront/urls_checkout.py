from django.urls import path
from .views.views import checkout_view, order_confirmation_view

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('order-confirmation/<int:order_id>/', order_confirmation_view, name='order_confirmation'),
]
