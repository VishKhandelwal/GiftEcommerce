from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import timedelta
import random

from accounts.models import CustomUser as User, UniqueCode
from orders.models import Order


# Utility: OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))


# Step 1: Login → Send OTP & Code
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'accounts/login.html', {'error': 'Email is required'})

        otp = generate_otp()

        user, _ = User.objects.get_or_create(email=email)
        user.otp = otp
        user.save()

        request.session['otp'] = otp
        request.session['email'] = email

        # Check if user already redeemed
        redeemed = Order.objects.filter(user=user).exists()
        request.session['already_redeemed'] = redeemed

        # Fetch or assign unique code
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        # Check if existing code is expired
        if code_obj and code_obj.assigned_time:
            expiry_time = code_obj.assigned_time + timedelta(days=14)
            if timezone.now() > expiry_time:
                code_obj.is_used = True
                code_obj.save()
                return render(request, "accounts/link_expired.html", {"email": email})

        # Try reusing old unused code
        if not code_obj:
            code_obj = UniqueCode.objects.filter(
                assigned_to=email,
                is_used=False,
                assigned_time__lt=timezone.now() - timedelta(days=14)
            ).first()

        # Try assigning a new unassigned code
        if not code_obj:
            code_obj = UniqueCode.objects.filter(assigned_to__isnull=True, is_used=False).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Still no code
        if not code_obj:
            return render(request, 'accounts/link_expired.html', {
                'email': email,
                'error': 'No unique codes available at the moment.'
            })

        # Send email with OTP + code
        context = {
            'otp': otp,
            'unique_code': code_obj.code,
        }
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)

        send_mail(
            subject="🎁 Redeem Your Gift Hamper - Team Infinity",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
        )

        return render(request, 'accounts/verify.html', {'email': email})

    return render(request, 'accounts/login.html')

otp_store = {}

def new_user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')

        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists. Please log in.")
            return redirect('accounts:login')

        otp = random.randint(100000, 999999)
        otp_store[email] = {
            'otp': str(otp),
            'full_name': full_name,
            'phone': phone
        }

        send_mail(
            subject="Your OTP for Infinity Box",
            message=f"Your OTP is {otp}",
            from_email='hello@theinfinitybox.in',
            recipient_list=[email]
        )

        request.session['email'] = email
        return redirect('accounts:verify_otp')

    return render(request, 'accounts/new_user.html')




# Step 2: OTP Verification + Consent
def verify_otp(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        email = request.session.get("email")
        agreed = request.POST.get("agree_terms")
        resend = request.POST.get("resend_otp")

        # If user clicked resend OTP
        if resend:
            from accounts.utils import send_otp_email  # ✅ Make sure you have a reusable send_otp_email function
            new_otp = send_otp_email(email)
            request.session['otp'] = new_otp
            return render(request, "accounts/verify.html", {
                "email": email,
                "success": "OTP resent successfully. Please check your inbox."
            })

        # Must agree to data policy
        if not agreed:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": "Please agree to the data policy to proceed."
            })

        # Check OTP
        if input_otp == session_otp and email:
            user, _ = User.objects.get_or_create(email=email)
            login(request, user)

            # Check if user already redeemed their code
            code = UniqueCode.objects.filter(assigned_to=email, is_used=True).first()
            if code:
                request.session['already_redeemed'] = True
                return redirect('orders:summary')

            return redirect("products:choose_box")

        return render(request, "accounts/verify.html", {
            "email": email,
            "error": "Invalid OTP. Please try again."
        })

    email = request.session.get("email")
    return render(request, "accounts/verify.html", {"email": email})

# Step 3: Resend OTP
def resend_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email or email.strip() == "":
            return render(request, "accounts/verify.html", {
                "error": "Email not provided or invalid."
            })

        otp = generate_otp()
        request.session["otp"] = otp
        request.session["email"] = email

        try:
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": f"Failed to send OTP: {str(e)}"
            })

        return render(request, "accounts/login.html", {
            "email": email,
            "message": "A new OTP has been sent to your email."
        })

    return redirect("accounts:login")


# Step 4: Logout
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
