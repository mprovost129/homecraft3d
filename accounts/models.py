from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for Home Craft 3D.

    Notes / invariants (enforced in save()):
    - If a user is marked as `is_owner`, we force `is_staff=True` so Django admin access aligns.
    - Roles are allowed to be multi-select (consumer + seller), but templates should prefer the
      helper properties (is_pure_consumer, is_seller_or_owner) to avoid brittle logic.
    """

    # Role flags
    is_seller = models.BooleanField(default=False)
    is_consumer = models.BooleanField(default=True)
    is_owner = models.BooleanField(default=False, help_text="Site owner/admin with full privileges")

    # Profile / contact
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # NOTE: For a marketplace checkout flow, you will likely want an Address model (one-to-many)
    # rather than a single address on the User. Keeping these for now since they already exist.
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
        ("auto", "Auto (System Preference)"),
    ]
    theme_preference = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        blank=True,
        default="",
        help_text="User's theme preference.",
    )

    # Notification preferences
    notify_reviews_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for reviews")
    notify_reviews_email = models.BooleanField(default=True, help_text="Email notifications for reviews")
    notify_orders_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for orders")
    notify_orders_email = models.BooleanField(default=True, help_text="Email notifications for orders")
    notify_admin_inapp = models.BooleanField(default=True, help_text="Show in-app notifications for admin actions")
    notify_admin_email = models.BooleanField(default=True, help_text="Email notifications for admin actions")

    # IMPORTANT:
    # Promo banner controls should be site-wide settings, not user settings.
    # These fields existed in your original file; leaving them in place to avoid migration churn.
    # Strong recommendation: move to a singleton SiteSettings model later.
    show_promo_banner = models.BooleanField(default=False, help_text="Show promo banner at top of site (owner only)")
    promo_banner_text = models.CharField(max_length=255, blank=True, default="", help_text="Custom promo banner text")

    def save(self, *args, **kwargs):
        # Keep Django admin privileges aligned with your app-level "owner" concept.
        if self.is_owner:
            self.is_staff = True
        super().save(*args, **kwargs)

    # ---- Template-safe helpers (use these in templates instead of complex boolean combos) ----
    @property
    def is_pure_consumer(self) -> bool:
        """Consumer-only user (not seller, not owner)."""
        return bool(self.is_consumer and (not self.is_seller) and (not self.is_owner))

    @property
    def is_seller_or_owner(self) -> bool:
        """User has seller-like capabilities (seller or owner)."""
        return bool(self.is_seller or self.is_owner)

    @property
    def avatar_url(self) -> str | None:
        """
        Preferred avatar URL, using User.profile_picture first, then ConsumerProfile.avatar if present.
        This helps avoid template drift while you decide on a single canonical image field.
        """
        if self.profile_picture:
            try:
                return self.profile_picture.url
            except Exception:
                return None
        # Fallback to consumer profile avatar if it exists
        cp = getattr(self, "consumer_profile", None) or getattr(self, "consumerprofile", None)
        if cp and getattr(cp, "avatar", None):
            try:
                return cp.avatar.url
            except Exception:
                return None
        return None


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    verified = models.BooleanField(default=False, help_text="Manually verified by staff")

    def __str__(self) -> str:
        return self.display_name or f"SellerProfile({self.user.pk})"


class ConsumerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="consumer_profile")
    display_name = models.CharField(max_length=100, blank=True)

    # NOTE: This overlaps with User.profile_picture. Keep for now (to avoid migration churn),
    # but long-term pick ONE canonical field (recommended: User.profile_picture) and remove the other.
    avatar = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    bio = models.TextField(blank=True)

    # JSON preferences (validate in forms/services so it doesn't become junk over time)
    preferences = models.JSONField(default=dict, blank=True)

    # Favorites / saved searches
    favorite_categories = models.ManyToManyField(
        "products.Category",
        blank=True,
        related_name="favored_by_consumers",
    )
    saved_searches = models.JSONField(default=list, blank=True, help_text="List of saved search queries")

    # Wishlist & downloads
    wishlist = models.OneToOneField("products.Wishlist", on_delete=models.SET_NULL, null=True, blank=True)
    download_history = models.ManyToManyField("orders.Download", blank=True, related_name="consumers")

    # Social
    social_links = models.JSONField(default=dict, blank=True, help_text="Social media links")

    verified = models.BooleanField(default=False, help_text="Manually verified by staff")

    def __str__(self) -> str:
        return self.display_name or f"ConsumerProfile({self.user.pk})"
