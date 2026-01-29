from django import forms
from .models import StorefrontSettings

class StorefrontSettingsForm(forms.ModelForm):
    class Meta:
        model = StorefrontSettings
        fields = ['featured_products_mode', 'theme_mode']
        widgets = {
            'featured_products_mode': forms.Select(attrs={'class': 'form-select'}),
            'theme_mode': forms.Select(attrs={'class': 'form-select'})
        }
