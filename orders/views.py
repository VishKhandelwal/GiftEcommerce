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

def track_order_view(request):
    order = None
    message = ""
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.filter(order_id=order_id).first()
        if not order:
            message = "Invalid Order ID"
    return render(request, 'orders/track_order.html', {'order': order, 'message': message})

def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


