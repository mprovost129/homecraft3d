from django.db import models
from .models_wishlist import Wishlist

class ProductVariant(models.Model):
    product = models.ForeignKey('Product', related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Variant name (e.g., Size, Color, Material)")
    value = models.CharField(max_length=100, help_text="Variant value (e.g., Large, Red, PLA)")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Optional price override for this variant")
    inventory = models.IntegerField(null=True, blank=True, help_text="Stock for this variant (optional)")
    class Meta:
        unique_together = ('product', 'name', 'value')

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    seller = models.ForeignKey('sellers.Seller', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    media = models.ManyToManyField('Media', blank=True)
    license = models.ForeignKey('License', on_delete=models.SET_NULL, null=True, blank=True)
    # New fields for 3D print store
    is_digital = models.BooleanField(default=False)
    is_physical = models.BooleanField(default=False)
    length_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    width_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    height_mm = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    draft = models.BooleanField(default=False, help_text="If checked, product is a draft and not visible to buyers.")
    inventory = models.IntegerField(null=True, blank=True, help_text="Stock for physical products. Leave blank for digital products.")
    # Tag support for advanced search
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags for search and filtering.")

    # Featured product logic
    featured_manual = models.BooleanField(default=False, help_text="Show as featured if checked")
    view_count = models.PositiveIntegerField(default=0, help_text="Auto-incremented on product view")
    purchase_count = models.PositiveIntegerField(default=0, help_text="Auto-incremented on purchase")
    meta_title = models.CharField(max_length=70, blank=True, null=True, help_text="SEO meta title (max 70 chars)")
    meta_description = models.CharField(max_length=160, blank=True, null=True, help_text="SEO meta description (max 160 chars)")

class Category(models.Model):
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0, help_text="Order for display")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, help_text="Optional category image.")

    class Meta:
        ordering = ['position', 'name']


class Media(models.Model):
    FILE_TYPE_CHOICES = [
        ('stl', 'STL'),
        ('obj', 'OBJ'),
        ('3mf', '3MF'),
        ('zip', 'ZIP'),
        ('step', 'STEP'),
        ('iges', 'IGES'),
        ('jpg', 'JPG'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
        # Add more as needed
    ]
    file = models.FileField(upload_to='product_files/', blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='stl')

class License(models.Model):
    name = models.CharField(max_length=100)
    terms = models.TextField()
