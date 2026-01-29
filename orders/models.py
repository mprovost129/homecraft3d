from django.db import models

class Order(models.Model):
    consumer = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Download(models.Model):
    line_item = models.ForeignKey(LineItem, on_delete=models.CASCADE)
    file = models.FileField(upload_to='product_files/')
    downloaded_at = models.DateTimeField(auto_now_add=True)
