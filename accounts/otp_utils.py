import random
from django.core.mail import send_mail
from .models import OTP
from django.utils import timezone
from datetime import timedelta

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email):
    otp_code = generate_otp()
    OTP.objects.update_or_create(
        email=email,
        defaults={'code': otp_code, 'created_at': timezone.now()}
    )
    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP is: {otp_code}',
        from_email='GiftBox <vaishali.kh2310@gmail.com>',
        recipient_list=[email],
        fail_silently=False,
    )
