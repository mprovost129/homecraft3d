from django.contrib import admin
from .models_collections import FeaturedCollection

@admin.register(FeaturedCollection)
class FeaturedCollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "position")
    list_editable = ("is_active", "position")
    search_fields = ("name",)
    filter_horizontal = ("products",)
    ordering = ("position",)
