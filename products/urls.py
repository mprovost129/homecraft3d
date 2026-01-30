from django.urls import path
app_name = 'products'
from .views import views
from .views.views import wishlist_view, add_to_wishlist, remove_from_wishlist
from django.urls import include

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),
    path('categories/reorder/<int:category_id>/<str:direction>/', views.category_reorder, name='category_reorder'),
    # Review URLs for product detail integration
    path('reviews/', include('reviews.urls')),
]
