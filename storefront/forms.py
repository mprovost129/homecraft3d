from django import forms
from .models import StorefrontSettings

SEARCH_TYPE_CHOICES = [
    ("models", "Models"),
    ("users", "Users"),
    ("collections", "Collections"),
    ("posts", "Posts"),
]

class AdvancedSearchForm(forms.Form):
    q = forms.CharField(label="Search", required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Search models, users, collections, posts...'
    }))
    type = forms.ChoiceField(label="Type", choices=[("all", "All")] + SEARCH_TYPE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    category = forms.CharField(label="Category", required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}))
    min_price = forms.DecimalField(label="Min Price", required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'}))
    max_price = forms.DecimalField(label="Max Price", required=False, min_value=0, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'}))
    sort = forms.ChoiceField(label="Sort By", required=False, choices=[
        ("relevance", "Relevance"),
        ("newest", "Newest"),
        ("popular", "Most Popular"),
        ("price_low", "Price: Low to High"),
        ("price_high", "Price: High to Low"),
    ], widget=forms.Select(attrs={'class': 'form-select'}))

class StorefrontSettingsForm(forms.ModelForm):
    class Meta:
        model = StorefrontSettings
        fields = ['featured_products_mode', 'theme_mode']
        widgets = {
            'featured_products_mode': forms.Select(attrs={'class': 'form-select'}),
            'theme_mode': forms.Select(attrs={'class': 'form-select'})
        }
