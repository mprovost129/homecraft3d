
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
import os
from .models import Product, ProductVariant, Media, Category
from .forms_mixins import VirusScanMixin
from moderation.models import SecuritySetting

# Product Variant Form
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'value', 'price', 'inventory']

# Inline formset for variants
ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True
)

# Category form for add/edit
class CategoryForm(forms.ModelForm):
    image = forms.ImageField(required=False, label="Category Image")
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image']

class ProductForm(forms.ModelForm):
    is_digital = forms.BooleanField(required=False, label="Digital Download (3D File)")
    is_physical = forms.BooleanField(required=False, label="Physical Object")
    length_mm = forms.DecimalField(max_digits=7, decimal_places=2, required=False, label="Length (mm)")
    width_mm = forms.DecimalField(max_digits=7, decimal_places=2, required=False, label="Width (mm)")
    height_mm = forms.DecimalField(max_digits=7, decimal_places=2, required=False, label="Height (mm)")
    draft = forms.BooleanField(required=False, label="Save as Draft")
    inventory = forms.IntegerField(required=False, label="Inventory (stock)", min_value=0, help_text="Required for physical products.")
    meta_title = forms.CharField(required=False, max_length=70, label="SEO Meta Title", help_text="Max 70 characters.")
    meta_description = forms.CharField(required=False, max_length=160, label="SEO Meta Description", widget=forms.Textarea(attrs={'rows':2}), help_text="Max 160 characters.")
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'license', 'draft', 'inventory', 'meta_title', 'meta_description']

    def clean_inventory(self):
        inventory = self.cleaned_data.get('inventory')
        is_physical = self.cleaned_data.get('is_physical')
        is_digital = self.cleaned_data.get('is_digital')
        # Only require inventory for physical products
        if is_physical and (inventory is None):
            raise ValidationError('Inventory is required for physical products.')
        if is_digital and not is_physical:
            return None
        return inventory


class MediaForm(VirusScanMixin, forms.ModelForm):
    file = forms.FileField(required=False)
    image = forms.ImageField(required=False)
    file_type = forms.ChoiceField(choices=Media.FILE_TYPE_CHOICES)

    class Meta:
        model = Media
        fields = ['file', 'image', 'file_type']

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        image = cleaned_data.get('image')
        file_type = cleaned_data.get('file_type')
        allowed_exts = dict(Media.FILE_TYPE_CHOICES).keys()
        # Fetch security settings from DB (admin editable)
        sec = SecuritySetting.objects.first()
        max_file_size_mb = sec.max_file_size_mb if sec else 20
        allowed_mime_types = sec.get_allowed_mime_types() if sec else [
            'application/sla', 'application/vnd.ms-pki.stl',
            'application/octet-stream', 'image/jpeg', 'image/png']
        if file:
            ext = os.path.splitext(file.name)[1][1:].lower()
            if ext not in allowed_exts:
                raise ValidationError(f"File type .{ext} is not allowed.")
            if file_type != ext:
                raise ValidationError(f"Selected file type does not match file extension.")
            # File size limit
            if file.size > max_file_size_mb * 1024 * 1024:
                raise ValidationError(f"File size exceeds {max_file_size_mb} MB limit.")
            # MIME type check
            if hasattr(file, 'content_type') and file.content_type not in allowed_mime_types:
                raise ValidationError(f"File MIME type {file.content_type} is not allowed.")
        if image:
            ext = os.path.splitext(image.name)[1][1:].lower()
            if ext not in allowed_exts:
                raise ValidationError(f"Image type .{ext} is not allowed.")
            if file_type != ext:
                raise ValidationError(f"Selected file type does not match image extension.")
            # File size limit
            if image.size > max_file_size_mb * 1024 * 1024:
                raise ValidationError(f"Image size exceeds {max_file_size_mb} MB limit.")
            # MIME type check
            if hasattr(image, 'content_type') and image.content_type not in allowed_mime_types:
                raise ValidationError(f"Image MIME type {image.content_type} is not allowed.")
        if not file and not image:
            raise ValidationError("You must upload a file or image.")
        return cleaned_data
