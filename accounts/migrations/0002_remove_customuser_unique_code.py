# Generated by Django 5.2.2 on 2025-06-12 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='unique_code',
        ),
    ]
