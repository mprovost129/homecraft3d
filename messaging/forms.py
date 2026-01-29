from django import forms
from .models import Message
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

class MessageForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(action='message'))
    class Meta:
        model = Message
        fields = ['body', 'captcha']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'}),
        }
