from django.db import models
from products.models import Product

class FeaturedCollection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    products = models.ManyToManyField(Product, blank=True)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0, help_text="Order for display (lower = first)")

    class Meta:
        ordering = ['position', 'name']

    def __str__(self):
        return self.name
