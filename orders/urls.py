from django.urls import path
from . import views
from .views import order_history_view

urlpatterns = [
    path('dashboard/', views.consumer_dashboard, name='consumer_dashboard'),
    path('history/', order_history_view, name='order_history'),
]
