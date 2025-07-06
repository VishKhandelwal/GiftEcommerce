from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .utils import send_tracking_email, send_otp_email


def send_otp_email(email, otp):
    subject = "Your Order Tracking OTP"
    message = f"Your OTP for tracking the order is: {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def send_tracking_email(order):
    subject = "🚚 Your Order Has Been Dispatched!"
    context = {
        'courier_name': order.courier_name,
        'tracking_number': order.tracking_number,
        'tracking_link': order.tracking_link,
        'estimated_delivery': order.estimated_delivery,
        'user_email': order.user.email,
    }

    html_message = render_to_string('emails/tracking_email.html', context)
    plain_message = render_to_string('emails/tracking_email.txt', context)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message
    )