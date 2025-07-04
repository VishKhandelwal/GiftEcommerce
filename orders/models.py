# orders/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.conf import settings

from products.models import Product

User = get_user_model()


def default_expected_delivery():
    return timezone.now().date() + timedelta(days=5)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.TextField(default="Not provided")
    otp = models.CharField(max_length=6, blank=True, null=True)  # Optional for tracking
    created_at = models.DateTimeField(auto_now_add=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.email if self.user else 'Guest'}"


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="orderitem", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')
    expected_delivery = models.DateField(default=default_expected_delivery, null=True, blank=True)
    tracking_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    courier_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.order.pk} - {self.product.name}"
