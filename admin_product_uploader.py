import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GiftEcommerce.settings')
django.setup()

from products.models import Product

# List of product details
data = [
    {
        "name": "Anniversary Combo Set",
        "description": "Cushion, mug, rose, chocolate set for your wife.",
        "price": 0,
        "filename": "gift1.jpg"
    },
    {
        "name": "Heart Photo Collage",
        "description": "Wall hanging with LED heart-shaped photo collage.",
        "price": 0,
        "filename": "gift2.jpg"
    },
    {
        "name": "Romantic Gift Hamper",
        "description": "Teddy, golden rose, necklace, and card combo.",
        "price": 0,
        "filename": "gift3.jpg"
    },
    {
        "name": "Chocolate Gift Basket",
        "description": "Basket with teddy, wine bottle, chocolates and plant.",
        "price": 0,
        "filename": "gift4.jpg"
    }
]

media_path = os.path.join(os.getcwd(), 'media', 'products')

for item in data:
    file_path = os.path.join(media_path, item["filename"])
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            image_file = File(f)
            product = Product(
                name=item["name"],
                description=item["description"],
                price=item["price"]
            )
            product.image.save(item["filename"], image_file, save=True)
            print(f"Uploaded: {product.name}")
    else:
        print(f"Image file not found: {file_path}")
