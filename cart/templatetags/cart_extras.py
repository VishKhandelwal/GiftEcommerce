from django import template

register = template.Library()

@register.filter
def calc_subtotal(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)


@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''