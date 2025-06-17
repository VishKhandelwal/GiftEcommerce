from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('T-shirts', 'T-shirts'),
        ('Notebooks', 'Notebooks'),
        ('Bottles', 'Bottles'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0)
    type = models.CharField(max_length=100, choices=[("T-shirts", "T-shirts"), ("Notebooks", "Notebooks"), ("Bottles", "Bottles")])
    image = models.ImageField(upload_to='products/')
    is_customizable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    category = models.CharField(max_length=100)  # e.g., "T-shirts", "Notebooks"
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    
class CustomBox(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    box_color = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    selected_items = models.ManyToManyField(Product, blank=True)
    

    def __str__(self):
        return f"CustomBox {self.id}"
    
class DeliveryAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, default="")
    phone_number = models.CharField(max_length=15, blank=True, default="")
    pincode = models.CharField(max_length=10, blank=True, default="")
    city = models.CharField(max_length=50, blank=True, default="")
    state = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.full_name} - {self.pincode}"


