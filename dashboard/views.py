from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from orders.models import Order
from products.models import Product
from django.db import models
from django.db.models import Sum



@staff_member_required
def dashboard_view(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    in_transit_orders = Order.objects.filter(status='in_transit').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)
