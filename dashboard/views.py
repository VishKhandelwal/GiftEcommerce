from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from orders.models import Order
from products.models import Product
from django.db import models
from django.db.models import Sum

@staff_member_required
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="Pending").count()
    processing_orders = Order.objects.filter(status="Processing").count()
    in_transit_orders = Order.objects.filter(status="In Transit").count()
    delivered_orders = Order.objects.filter(status="Delivered").count()

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin/admin_dashboard.html', context)
