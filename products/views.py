from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from collections import defaultdict
import uuid
from django.conf import settings
from .models import Product
from django.http import HttpResponseBadRequest
from .forms import DeliveryAddressForm
from orders.models import Order, OrderItem
from django.utils import timezone
from datetime import timedelta
from cart.models import CartItem

@login_required(login_url='accounts:login')
def choose_box(request):
    black_box, _ = Product.objects.get_or_create(
        name="Black Signature Box",
        type="Box",
    
    )

    white_box, _ = Product.objects.get_or_create(
        name="White Signature Box",
        type="Box",

    )

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id, type='Box')
        box_color = request.POST.get('box_color')
    
        CartItem.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        request.session['box_color'] = box_color
        return redirect('products:choose_items')

    return render(request, 'products/choose_box.html', {
        'black_box': black_box,
        'white_box': white_box,
    })



from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
import json
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
import json
from .models import Product, CartItem  # Adjust import as per your app

@login_required(login_url='accounts:login')
def choose_items(request):
    allowed_categories = ['T-shirts', 'Notebooks', 'Bottles']
    selected_category = request.GET.get('category', allowed_categories[0])

    if request.method == 'POST':
        selected_category = request.POST.get('category', allowed_categories[0])

        if selected_category not in allowed_categories:
            selected_category = allowed_categories[0]

        product_id = request.POST.get('product_id')
        if not product_id:
            messages.error(request, "Invalid product selection.")
            return redirect(f"{request.path}?category={selected_category}")

        # Check if already one item from this category exists in the cart
        if CartItem.objects.filter(user=request.user, product__type=selected_category).exists():
            messages.error(request, f"You can only add one item from {selected_category}.")
            return redirect(f"{request.path}?category={selected_category}")

        # Fetch the product and add it to cart
        product = get_object_or_404(Product, id=product_id, type=selected_category)
        CartItem.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )

        return redirect(f"{request.path}?category={selected_category}")

    if selected_category not in allowed_categories:
        selected_category = allowed_categories[0]

    products = Product.objects.filter(type=selected_category)
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.calc_subtotal() for item in cart_items)

    cart_items_json = json.dumps([
        {'id': item.id, 'name': item.product.name, 'category': item.product.type}
        for item in cart_items
    ])

    return render(request, 'products/choose_items.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'categories': allowed_categories,
        'selected_category': selected_category,
        'cart_items_json': mark_safe(cart_items_json),
    })





@login_required(login_url='accounts:login')  # Ensure only logged-in users access this
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        category = product.type
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            quantity = 1

        # Rule 1: Limit total items in cart
        cart_items_count = CartItem.objects.filter(user=request.user).count()
        if cart_items_count >= 4:  # If including Box, change to 4
            messages.warning(request, "You can only add up to 4 items in total.")
            return redirect('products:choose_items')

        # Rule 2: Only one item per category
        if CartItem.objects.filter(user=request.user, product__type=category).exists():
            messages.warning(request, f"You can only add one product from '{category}'.")
            return redirect('products:choose_items')

        # Rule 3: For Box type, force quantity = 1 and size = None
        if category == 'Box':
            quantity = 1
            size = None

        # Add to cart
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
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'products:choose_items')


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
    })
    return JsonResponse({'html': html})


def magic_created(request):
    steps = [
        ('1', 'CHOOSE YOUR BOX COLOR'),
        ('2', 'CHOOSE YOUR ITEMS'),
        ('3', 'MAGIC CREATED!')
    ]
    return render(request, 'products/magic_created.html', {'steps': steps})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from cart.models import CartItem

@login_required
def order_preview(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('products:choose_box')  # Redirect to box selection if cart is empty

    # Categorize selections
    selected_items = {
        "Box": cart_items.filter(product__type__icontains='box').first(),
        "Bottles": cart_items.filter(product__type__icontains='bottles').first(),
        "T-shirts": cart_items.filter(product__type__icontains='t-shirt').first(),
        "Notebooks": cart_items.filter(product__type__icontains='notebooks').first(),
        "AutoIncluded": ["Stickers", "Welcome Note"]  # You can replace or customize this
    }

    return render(request, "cart/order_preview.html", {
        "selected_items": selected_items,
        "cart_items": cart_items,
    })


def generate_unique_order_id():
    return str(uuid.uuid4()).replace("-", "").upper()[:12]


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return redirect('cart:view_cart')

    total = sum(item.calc_subtotal() for item in cart_items)

    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            # Proceed to order creation after saving address
            return redirect('products:checkout_success')
    else:
        form = DeliveryAddressForm()

    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'form': form,
    })



def checkout_success(request):
    user = request.user
    items = CartItem.objects.filter(user=user)

    if not items.exists():
        return redirect('products:view_cart')

    

    # ✅ Create the order
    order = Order.objects.create(
        user=user,
     # Make sure the Order model has this field
    )

    # ✅ Add dispatch logic
    now = timezone.localtime()
    if now.hour < 14:
        dispatch_date = now.date()
    else:
        dispatch_date = now.date() + timedelta(days=1)

    order.estimated_delivery = dispatch_date + timedelta(days=3)  # 3-day delivery
    order.save()

    # ✅ Create Order Items
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            user=user,
            status='in_transit'
        )

    # ✅ Clear the cart
    items.delete()

    # ✅ Store info in session
    request.session['order_id'] = order.id

    # ✅ Send confirmation email
    if user.email:
        try:
            send_mail(
                subject='Your Order Confirmation',
                message=f'''Thank you for your purchase!

Order ID: {order.id}
Courier: To be updated soon
Estimated Delivery: {order.estimated_delivery.strftime('%d %b %Y')}
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email send failed:", e)

    return render(request, 'cart/checkout_success.html', {'order': order})
