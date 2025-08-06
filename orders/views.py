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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Order, OrderItem

@login_required(login_url='accounts:login')


def order_summary_view(request):
    user = request.user

    # Get the most recent order for this user
    latest_order = Order.objects.filter(user=user).order_by('-created_at').first()

    if not latest_order:
        return render(request, 'orders/summary.html', {
            'error': 'No order found for this user.'
        })

    # Get all hamper items (products) in that order
    hamper_items = OrderItem.objects.filter(order=latest_order)

    return render(request, 'orders/summary.html', {
        'order': latest_order,
        'hamper_items': hamper_items
    })



def track_order_view(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')

        try:
            order = Order.objects.get(id=order_id)
            return render(request, 'orders/order_tracking_result.html', {'order': order})
        except Order.DoesNotExist:
            return render(request, 'orders/track_order.html', {
                'error': 'Invalid Order ID. Please try again.'
            })

    return render(request, 'orders/track_order.html')

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



