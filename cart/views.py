from django.shortcuts import render, redirect, get_object_or_404
from cart.models import CartItem
from products.models import Product
from django.contrib import messages

# View cart
from collections import defaultdict
from cart.models import CartItem

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



# Add to cart (via POST or direct call)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Item added to cart.")
    return redirect('cart:cart')

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
            item.delete()  # auto-remove if quantity goes to 0

    return redirect('cart:cart')


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
