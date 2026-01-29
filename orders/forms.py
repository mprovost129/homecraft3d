from django import forms
from .models import Order

class RefundRequestForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    reason = forms.CharField(widget=forms.Textarea, label="Reason for refund")
