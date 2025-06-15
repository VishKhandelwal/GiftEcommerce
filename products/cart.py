from django.shortcuts import get_object_or_404, redirect
from products.models import Product
from cart.models import CartItem
from django.shortcuts import render

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.quantity += 1
    item.save()
    return redirect('cart:cart')

def view_cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    discount = 0
    shipping = 90 if subtotal < 1000 else 0
    gst = int(subtotal * 0.18)
    total = subtotal - discount + shipping + gst

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'gst': gst,
        'total': total,
        'addresses': [],  # Load from Address model if available
    }
    return render(request, 'cart/cart.html', context)