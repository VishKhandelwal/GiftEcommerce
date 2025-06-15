from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from products.models import Product
from accounts.models import CustomUser
from django.conf import settings


User = get_user_model()

# Shared status choices
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('in_transit', 'In Transit'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

def default_expected_delivery():
    return timezone.now().date() + timedelta(days=5)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6, default='000000')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    courier_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')

    def __str__(self):
        return f"Order {self.order_id} - {self.status}"


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="orderitem", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_transit')
    expected_delivery = models.DateField(default=default_expected_delivery, null=True, blank=True)
    tracking_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default
    courier_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.order.order_id} - {self.product.name}"
