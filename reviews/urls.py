from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('create/<int:product_id>/', views.review_create, name='review_create'),
    path('edit/<int:review_id>/', views.review_edit, name='review_edit'),
    path('delete/<int:review_id>/', views.review_delete, name='review_delete'),
]
