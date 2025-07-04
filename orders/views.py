from django.shortcuts import render
from .models import Order
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
import json
import random
from django.shortcuts import render
from orders.models import Order
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count
from django.contrib.admin.views.main import ChangeList
from django.contrib import admin
from .models import Order

def order_summary_view(request):
    latest_order = Order.objects.filter(user=request.user).last()
    return render(request, 'orders/summary.html', {
        'order': latest_order
    })


def track_order_view(request):
    try:
        order = Order.objects.filter(user=request.user).latest('order_date')
    except Order.DoesNotExist:
        order = None

    return render(request, 'orders/track_order.html', {
        'order': order
    })

def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

from django.shortcuts import render

def admin_dashboard(request):
    from orders.models import Order  # Lazy import avoids circular dependency

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    in_transit_orders = Order.objects.filter(status='in_transit').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)



