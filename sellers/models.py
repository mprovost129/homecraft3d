from django.db import models

class Seller(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    stripe_account_id = models.CharField(max_length=255, blank=True)

class StripeAccount(models.Model):
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=255)
    details_submitted = models.BooleanField(default=False)
