from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('start/<int:user_id>/', views.start_thread, name='start_thread'),
]
