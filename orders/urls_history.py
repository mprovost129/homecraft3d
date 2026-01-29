from django.urls import path
from .views.order_history import order_history_view

urlpatterns = [
    path('history/', order_history_view, name='order_history'),
]
