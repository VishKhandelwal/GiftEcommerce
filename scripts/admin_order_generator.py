import os
import django
from django.utils import timezone
from django.core.management.utils import get_random_string
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GiftEcommerce.settings')
django.setup()

from orders.models import Order
from products.models import Product
from accounts.models import User

# Create test user (if not exists)
user, created = User.objects.get_or_create(email='testuser@example.com')

# Select existing products
products = Product.objects.all()
if not products:
    print("No products found. Please run the product uploader first.")
    exit()

# Create a test order
for i in range(1, 3):
    order_id = get_random_string(10).upper()
    otp = str(random.randint(100000, 999999))
    product = random.choice(products)

    Order.objects.create(
        user=user,
        order_id=order_id,
        product=product,
        quantity=1,
        status=random.choice(['PENDING', 'PROCESSING', 'DISPATCHED']),
        expected_delivery=timezone.now().date() + timezone.timedelta(days=random.randint(3, 7)),
        courier_name="BlueDart",
        tracking_link="https://bluedart.com/tracking/" + order_id,
        otp=otp
    )

    print(f"✅ Created Order: {order_id} | OTP: {otp} | Product: {product.name}")