# orders/admin.py
from django.contrib import admin
from .models import Order
from django.utils.html import format_html

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'user__email']

    change_list_template = "admin/orders/order_change_list.html"  # Custom dashboard
