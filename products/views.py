from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from collections import defaultdict
import uuid

from .models import Product
from cart.models import CartItem
from .forms import DeliveryAddressForm
from orders.models import Order, OrderItem


@login_required
def choose_box(request):
    if request.method == 'POST':
        request.session['box_color'] = request.POST['box_color']
        return redirect('products:choose_items')
    return render(request, 'products/choose_box.html')


def choose_items(request):
    selected_category = request.GET.get('category', 'T-shirts')  # Default: T-shirts
    categories = ['T-shirts', 'Notebooks', 'Bottles']
    products = Product.objects.filter(type=selected_category)
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.calc_subtotal() for item in cart_items)

    return render(request, 'products/choose_items.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'categories': categories,
        'selected_category': selected_category,
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        category = product.type
        size = request.POST.get('size')  # 🔸 Get size if submitted

        # ✅ Rule 1: Limit total cart items to 3
        cart_items_count = CartItem.objects.filter(user=request.user).count()
        if cart_items_count > 4:
            messages.warning(
                request,
                "You can only add 3 items in total. Please remove an item to add another."
            )
            return redirect('products:choose_items')

        # ✅ Rule 2: Only one product per category
        if CartItem.objects.filter(user=request.user, product__type=category).exists():
            messages.warning(
                request,
                f"You can only add one product from the '{category}' category. "
                "Please remove the existing item to add another."
            )
            return redirect('products:choose_items')

        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        # 🔸 Save size if provided
        CartItem.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            size=size
        )

        messages.success(request, f"{product.name} added to cart.")
        return redirect('products:choose_items')

    return redirect('products:choose_items')





def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.name} removed from cart.")
    return redirect('products:choose_items')


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
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, "Cart cleared.")
    return redirect('cart:cart')


def cart_summary_ajax(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.product.price for item in cart_items)
    html = render_to_string('products/cart_summary.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })
    return JsonResponse({'html': html})


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