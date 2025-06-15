from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
import random
from cart.models import CartItem
from orders.models import Order
import razorpay
from django.conf import settings

def checkout_view(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)

    if request.method == 'POST':
        for item in items:
            order_id = get_random_string(10).upper()
            otp = str(random.randint(100000, 999999))
            expected_delivery = timezone.now().date() + timezone.timedelta(days=5)

            Order.objects.create(
                user=request.user,
                order_id=order_id,
                product=item.product,
                quantity=item.quantity,
                status='PENDING',
                expected_delivery=expected_delivery,
                courier_name="Delhivery",
                tracking_link=f"https://courier.example.com/track/{order_id}",
                otp=otp
            )
            

            # Send order confirmation and OTP email
            send_mail(
                subject='Your Order Confirmation',
                message=f'Thank you for your purchase!\nOrder ID: {order_id}',
                from_email='vaishali.kh2310@gmail.com',
                recipient_list=[request.user.email],
                fail_silently=True,
            )

        items.delete()
        return render(request, 'cart/checkout.html')

    return render(request, 'cart/checkout_success.html', {'items': items, 'total': total})

