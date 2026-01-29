from django import forms
from .models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_picture', 'first_name', 'last_name', 'email', 'phone_number', 'address1', 'address2', 'city', 'state', 'zip_code'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


# Seller profile form for editing seller-specific fields
from .models import SellerProfile, ConsumerProfile

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['display_name', 'bio']


# Consumer profile form for editing consumer-specific fields
class ConsumerProfileForm(forms.ModelForm):
    class Meta:
        model = ConsumerProfile
        fields = ['preferences']

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='register'))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_picture', 'email',
            'notify_reviews_inapp', 'notify_reviews_email',
            'notify_orders_inapp', 'notify_orders_email',
            'notify_admin_inapp', 'notify_admin_email',
        ]

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='login'))
