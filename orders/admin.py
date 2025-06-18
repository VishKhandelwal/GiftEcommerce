# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'order_date')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'shipping_address')


    change_list_template = "admin/orders/order_change_list.html"  # Custom dashboard
