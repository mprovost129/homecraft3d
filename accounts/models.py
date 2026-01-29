from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=True)
    is_owner = models.BooleanField(default=False, help_text="Site owner/admin with full privileges")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    # Theme preference: light, dark, auto, or empty (use site default)
    THEME_CHOICES = [
        ("", "Use Site Default"),
        ("light", "Light Mode"),
        ("dark", "Dark Mode"),
        ("auto", "Auto (System Preference)")
    ]
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, blank=True, default="", help_text="User's theme preference.")
    # Notification preferences
    notify_reviews_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for reviews")
    notify_reviews_email = models.BooleanField(default=True, help_text="Email notifications for reviews")
    notify_orders_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for orders")
    notify_orders_email = models.BooleanField(default=True, help_text="Email notifications for orders")
    notify_admin_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for admin actions")
    notify_admin_email = models.BooleanField(default=True, help_text="Email notifications for admin actions")

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

class ConsumerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict, blank=True)
