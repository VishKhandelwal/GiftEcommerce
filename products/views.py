from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
import random
from .forms import DeliveryAddressForm
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from .models import CustomBox
from .models import Product
from cart.models import CartItem
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from .models import DeliveryAddress
from orders.models import Order, OrderItem 




def product_custom_flow(request):
    return render(request, 'products/product_custom_flow.html')

@login_required
def choose_box(request):
    if request.method == 'POST':
        request.session['box_color'] = request.POST['box_color']
        return redirect('products:choose_items')
    return render(request, 'products/choose_box.html')


def choose_items(request):
    category = request.GET.get('category')  # e.g., "T-shirts", "Notebooks", etc.

    if category:
        products = Product.objects.filter(type=category)
    else:
        products = Product.objects.filter(type__in=['T-shirts', 'Notebooks', 'Water Bottles'])

    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.calc_subtotal() for item in cart_items)

    return render(request, 'products/choose_items.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'selected_category': category,  # For highlighting the selected filter button in HTML
    })



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
        }

    request.session['cart'] = cart
    return redirect('products: cart_summary_ajax')


def cart_summary_ajax(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.product.price for item in cart_items)
    html = render_to_string('products/cart_summary.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })
    return JsonResponse({'html': html})

from collections import defaultdict

def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    grouped_cart = defaultdict(list)

    for item in cart_items:
        category = item.product.category
        if category:  # ✅ check if category is not None
            grouped_cart[category.name].append(item)

    context = {
        'cart_items': cart_items,
        'grouped_cart': grouped_cart,
    }
    return render(request, 'cart/cart.html', context)



# Update item quantity (increment/decrement)
def update_cart_item(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if action == 'increment':
        item.quantity += 1
        item.save()
    elif action == 'decrement':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

    return redirect('products:choose_items')

# Remove item from cart
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:cart')


# Clear all items in cart
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Cart cleared.")
    return redirect('cart:cart')


def magic_created(request):
    steps = [
        ('1', 'CHOOSE YOUR BOX COLOR'),
        ('2', 'CHOOSE YOUR ITEMS'),
        ('3', 'MAGIC CREATED!')
    ]
    return render(request, 'products/magic_created.html', {'steps': steps})



def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.calc_subtotal() for item in cart_items)

    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            # Proceed to payment or order summary
            return redirect('products:checkout_success')
    else:
        form = DeliveryAddressForm()

    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    return render(request, 'cart/checkout.html', context)

from django.core.mail import send_mail
from django.shortcuts import render, redirect

import uuid

def generate_unique_order_id():
    return str(uuid.uuid4()).replace("-", "").upper()[:12]  # e.g., 'A1B2C3D4E5F6'

def checkout_success(request):
    user = request.user
    items = user.cart_items.all()
    total = sum(item.calc_subtotal() for item in items)

    # Step 1: Generate OTP and unique order_id
    otp = get_random_string(6, allowed_chars='0123456789')
    order_id = generate_unique_order_id()
    while Order.objects.filter(order_id=order_id).exists():
        order_id = generate_unique_order_id()

    # Step 2: Create Order
    order = Order.objects.create(user=user, total=total, otp=otp, order_id=order_id)

    # Step 3: Create Order Items
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            status='in_transit', 
            price=item.product.price,
            user=request.user, 
        )

    # Step 4: Clear the cart
    items.delete()

    # Step 5: Store order ID and OTP in session (optional)
    request.session['order_id'] = order.id
    request.session['otp'] = otp

    # Step 6: Send confirmation email
    send_mail(
        subject='Your Order Confirmation',
        message=f'Thank you for your purchase!\nOrder ID: {order.order_id}\nOTP for tracking: {otp}',
        from_email='hello@theinfinitybox.in',
        recipient_list=[user.email],
        fail_silently=True,
    )

    return render(request, 'cart/checkout_success.html', {'order': order})



