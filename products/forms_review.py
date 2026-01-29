from django import forms
from .models_review import ProductReview
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class ProductReviewForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='review'))
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'body', 'captcha']
        widgets = {
            'rating': forms.Select(choices=[(x/2, f'{x/2} stars') for x in range(2, 11)]),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review title'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review...'}),
        }
