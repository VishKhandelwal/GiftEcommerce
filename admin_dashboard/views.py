from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from orders.models import Order
from products.models import Product
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_staff

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard:dashboard')  # Adjust as needed
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, "admin_dashboard/login.html")

@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    in_transit_orders = Order.objects.filter(status='in_transit').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    recent_orders = Order.objects.filter(order_date__isnull=False).order_by('-order_date')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
        'recent_orders': recent_orders,
    }

    return render(request, 'admin_dashboard/dashboard.html', context)  # <-- Fixed line

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

