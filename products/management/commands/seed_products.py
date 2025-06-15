# products/management/commands/seed_products.py
import os
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
from django.core.files import File

class Command(BaseCommand):
    help = 'Seed sample products with images from media/products/'

    def handle(self, *args, **kwargs):
        image_dir = os.path.join(settings.MEDIA_ROOT, 'products')

        if not os.path.exists(image_dir):
            self.stdout.write(self.style.ERROR('media/products/ folder does not exist'))
            return

        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if not image_files:
            self.stdout.write(self.style.WARNING('No images found in media/products/'))
            return

        for i, image_name in enumerate(image_files):
            name = f"Gift {i + 1}"
            price = random.randint(299, 999)
            description = "Auto-added gift product for demo purposes."

            with open(os.path.join(image_dir, image_name), 'rb') as img_file:
                product = Product(
                    name=name,
                    description=description,
                    price=price,
                )
                product.image.save(image_name, File(img_file), save=True)

            self.stdout.write(self.style.SUCCESS(f'Created: {name}'))

        self.stdout.write(self.style.SUCCESS('✅ Sample products added successfully.'))