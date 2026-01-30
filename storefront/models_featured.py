from django.db import models
from django.conf import settings

class FeaturedCreator(models.Model):
    seller = models.OneToOneField('sellers.Seller', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, help_text="Show this creator as featured")
    position = models.PositiveIntegerField(default=0, help_text="Order for display (lower = first)")
    note = models.CharField(max_length=255, blank=True, help_text="Optional note or tagline")

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"Featured: {self.seller.user.username}"