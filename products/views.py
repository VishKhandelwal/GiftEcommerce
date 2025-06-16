from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from collections import defaultdict
import uuid

from .models import Product, CustomBox, DeliveryAddress
from .forms import DeliveryAddressForm
from cart.models import CartItem
from orders.models import Order, OrderItem


@login_required
def choose_box(request):
    if request.method == 'POST':
        request.session['box_color'] = request.POST['box_color']
        return redirect('products:choose_items')
    return render(request, 'products/choose_box.html')

def choose_items(request):  # default is T-shirt
    products = Product.objects.filter(type__in=['T-shirts', 'Notebooks', 'Water Bottles'])
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.calc_subtotal() for item in cart_items)
    categories = ['T-shirts', 'Notebooks', 'Water Bottles']

    return render(request, 'products/choose_items.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'categories': categories,
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})

        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session['cart'] = cart

        return redirect('products:choose_items')  # Redirect to refresh cart display

def cart_summary_ajax(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.product.price for item in cart_items)
    html = render_to_string('products/cart_summary.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })
    return JsonResponse({'html': html})

def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    grouped_cart = defaultdict(list)

    for item in cart_items:
        if item.product.category:
            grouped_cart[item.product.category.name].append(item)

    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'grouped_cart': grouped_cart,
    })


@login_required
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


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:cart')


@login_required
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


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.calc_subtotal() for item in cart_items)

    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('products:checkout_success')
    else:
        form = DeliveryAddressForm()

    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    })


def generate_unique_order_id():
    return str(uuid.uuid4()).replace("-", "").upper()[:12]


@login_required
def checkout_success(request):
    user = request.user
    items = user.cart_items.all()
    total = sum(item.calc_subtotal() for item in items)

    otp = get_random_string(6, allowed_chars='0123456789')
    order_id = generate_unique_order_id()
    while Order.objects.filter(order_id=order_id).exists():
        order_id = generate_unique_order_id()

    order = Order.objects.create(user=user, total=total, otp=otp, order_id=order_id)

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            status='in_transit',
            price=item.product.price,
            user=user,
        )

    items.delete()
    request.session['order_id'] = order.id
    request.session['otp'] = otp

    send_mail(
        subject='Your Order Confirmation',
        message=f'Thank you for your purchase!\nOrder ID: {order.order_id}\nOTP for tracking: {otp}',
        from_email='hello@theinfinitybox.in',
        recipient_list=[user.email],
        fail_silently=True,
    )

    return render(request, 'cart/checkout_success.html', {'order': order})