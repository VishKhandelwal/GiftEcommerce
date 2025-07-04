from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta
import random
from orders.models import Order

from accounts.models import UniqueCode
from accounts.models import CustomUser as User
from accounts.utils.unique_code import assign_unique_code_to_email




def generate_otp():
    return str(random.randint(100000, 999999))

User = get_user_model()

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

        # Fetch or assign a unique code
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        if code_obj and code_obj.assigned_time:
            expiry_time = code_obj.assigned_time + timedelta(days=14)
            if timezone.now() > expiry_time:
                # Code expired
                code_obj.is_used = True
                code_obj.save()
                return render(request, "accounts/link_expired.html", {"email": email})

        # Reuse expired assigned code (optional)
        if not code_obj:
            code_obj = UniqueCode.objects.filter(
                assigned_to=email,
                is_used=False,
                assigned_time__lt=timezone.now() - timedelta(days=14)
            ).first()

        # Assign new fresh code
        if not code_obj:
            code_obj = UniqueCode.objects.filter(
                assigned_to__isnull=True,
                is_used=False
            ).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Still no code available (optional fallback)
        if not code_obj:
            return render(request, 'accounts/link_expired.html', {
                'email': email,
                'error': 'No unique codes available at the moment.'
            })

        # Email context
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
            fail_silently=False,
        )

        return render(request, 'accounts/verify.html', {'email': email})

    return render(request, 'accounts/login.html')

# Step 2: OTP Verification + Consent
from django.urls import reverse

def verify_otp(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        email = request.session.get("email")
        agreed = request.POST.get("agree_terms")

        if not agreed:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": "Please agree to the data policy to proceed."
            })

        if input_otp == session_otp and email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(email=email, username=email)

            login(request, user)

            # 🔁 Check if user already redeemed their code
            from accounts.models import UniqueCode
            code = UniqueCode.objects.filter(assigned_to=email, is_used=True).first()

            if code:
                request.session['already_redeemed'] = True
                return redirect('orders:summary')  # redirects to Order Summary

            return redirect("products:choose_box")
        else:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": "Invalid OTP"
            })

    return render(request, "accounts/verify.html")


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
                fail_silently=False,
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
