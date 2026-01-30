from django.contrib import admin
from .models_featured import FeaturedCreator

@admin.register(FeaturedCreator)
class FeaturedCreatorAdmin(admin.ModelAdmin):
    list_display = ("seller", "is_active", "position", "note")
    list_editable = ("is_active", "position", "note")
    search_fields = ("seller__user__username",)
    ordering = ("position",)
