from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'featured_manual', 'view_count', 'purchase_count')
    list_filter = ('featured_manual', 'category')
    search_fields = ('name', 'description')
    list_editable = ('featured_manual',)
