from django.contrib import admin
from .models_review import ProductReview

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "is_hidden", "created_at")
    list_filter = ("is_approved", "is_hidden", "rating", "created_at")
    search_fields = ("product__name", "user__username", "title", "body")
    actions = ["approve_reviews", "hide_reviews"]

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True, is_hidden=False)
        self.message_user(request, f"{updated} review(s) approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def hide_reviews(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"{updated} review(s) hidden.")
    hide_reviews.short_description = "Hide selected reviews"