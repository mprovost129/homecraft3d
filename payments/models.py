from django.db import models

class Payout(models.Model):
    seller = models.ForeignKey('sellers.Seller', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Fee(models.Model):
    payout = models.ForeignKey(Payout, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
