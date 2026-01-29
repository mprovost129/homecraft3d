from django.urls import path
from . import views

from .stripe_checkout import create_checkout_session
from .webhooks import stripe_webhook

urlpatterns = [
    path('checkout/', create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]
