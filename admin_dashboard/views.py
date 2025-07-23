from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime

from orders.models import Order
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

# ✅ Check if user is admin
def is_admin(user):
    return user.is_staff

# ✅ Admin Login View
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "admin_dashboard/login.html")

# ✅ Admin Dashboard View
@login_required(login_url='admin_dashboard:admin_login')
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Filters
    month = request.GET.get('month')
    year = request.GET.get('year')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')  # pending, processing, in_transit, delivered

    orders = Order.objects.all()

    if month:
        orders = orders.filter(order_date__month=int(month))
    if year:
        orders = orders.filter(order_date__year=int(year))
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            orders = orders.filter(order_date__range=[start, end])
        except ValueError:
            messages.error(request, "Invalid date format.")
    if status:
        orders = orders.filter(status=status)

    # Stats
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    processing_orders = orders.filter(status='processing').count()
    in_transit_orders = orders.filter(status='in_transit').count()
    delivered_orders = orders.filter(status='delivered').count()

    context = {
        'orders': orders.order_by('-order_date'),
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
        'selected_month': month,
        'selected_year': year,
        'selected_status': status,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'admin_dashboard/dashboard.html', context)

def manual_order_entry(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        user, created = User.objects.get_or_create(email=email)

        Order.objects.create(
            user=user,
            status=status,
            order_date=timezone.now(),
            notes=notes
        )

        messages.success(request, f"Order for {email} created successfully.")
        return redirect('admin_dashboard:manual_order_entry')

    return render(request, 'admin_dashboard/manual_order_entry.html')

# ✅ Admin Logout View
def admin_logout(request):
    logout(request)
    return redirect('admin_dashboard:admin_login')
