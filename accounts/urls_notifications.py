from django.urls import path
from .views_notification import notifications_list, mark_notification_read

urlpatterns = [
    path('notifications/', notifications_list, name='notifications'),
    path('notifications/read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
]
