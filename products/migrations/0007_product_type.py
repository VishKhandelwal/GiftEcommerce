# Generated by Django 5.2.2 on 2025-06-12 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='type',
            field=models.CharField(choices=[('T-shirt', 'T-shirt'), ('Notebook', 'Notebook'), ('Cap', 'Cap')], default=2, max_length=100),
            preserve_default=False,
        ),
    ]
