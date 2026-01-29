from django import forms
from .models_rating import SellerRating

class SellerRatingForm(forms.ModelForm):
    class Meta:
        model = SellerRating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
