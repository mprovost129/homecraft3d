from django.db import models

class StorefrontSettings(models.Model):
    FEATURED_MODE_CHOICES = [
        ("manual", "Manual (admin checkmark)"),
        ("most_viewed", "Most Viewed"),
        ("most_purchased", "Most Purchased"),
    ]
    THEME_MODE_CHOICES = [
        ("light", "Light Mode"),
        ("dark", "Dark Mode"),
        ("auto", "Auto (System Preference)"),
    ]
    featured_products_mode = models.CharField(
        max_length=20,
        choices=FEATURED_MODE_CHOICES,
        default="manual",
        help_text="How to select featured products for the storefront."
    )
    theme_mode = models.CharField(
        max_length=10,
        choices=THEME_MODE_CHOICES,
        default="auto",
        help_text="Site theme: light, dark, or auto."
    )
    class Meta:
        verbose_name = "Storefront Setting"
        verbose_name_plural = "Storefront Settings"

    def __str__(self):
        return f"Storefront Settings (Featured: {self.featured_products_mode})"
