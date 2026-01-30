from django.db import models
from accounts.models import User
from products.models import Product

class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    products = models.ManyToManyField(Product, related_name='collections')
    is_public = models.BooleanField(default=True, help_text="Shareable and visible to others")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    share_uuid = models.CharField(max_length=36, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        import uuid
        if not self.share_uuid:
            self.share_uuid = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def get_share_url(self):
        return f"/collections/share/{self.share_uuid}/"

    def __str__(self):
        return self.name
