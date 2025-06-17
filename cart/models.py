from django.db import models
from django.conf import settings
from products.models import Product
from django.utils import timezone

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items',
        related_query_name='cart_item'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        related_query_name='cart_item'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=10, null=True, blank=True)  # <-- Add this


    def calc_subtotal(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) for {self.user.email}"
