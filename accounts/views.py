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

User = get_user_model()


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            return render(request, 'accounts/login.html', {'error': 'Email is required'})

        user, _ = User.objects.get_or_create(email=email)
        request.session['email'] = email

        # 🔒 Check if user has already redeemed an order
        if Order.objects.filter(user=user).exists():
            messages.info(request, "You’ve already redeemed your joining kit. Below is your order summary.")
            return redirect('orders:summary')  # ✅ Replace with actual view name

        # 🚀 Generate and assign OTP
        otp = generate_otp()
        user.otp = otp
        user.save()
        request.session['otp'] = otp

        # 🔑 Assign or reuse redemption code
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        if code_obj and code_obj.assigned_time:
            expiry_time = code_obj.assigned_time + timedelta(days=14)
            if timezone.now() > expiry_time:
                code_obj.is_used = True
                code_obj.save()
                return render(request, "accounts/link_expired.html", {"email": email})

        # If no usable code exists, assign a new one
        if not code_obj:
            code_obj = UniqueCode.objects.filter(assigned_to__isnull=True, is_used=False).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Final fallback: still no code
        if not code_obj:
            return render(request, 'accounts/link_expired.html', {
                'email': email,
                'error': 'No unique codes available at the moment.'
            })

        # 📧 Send OTP + code via email
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


def new_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, "Email is required.")
            return redirect('accounts:new_user')

        user = User.objects.filter(email=email).first()

        # ✅ Already registered
        if user:
            # 🔁 Already placed order? Redirect to summary
            if Order.objects.filter(user=user).exists():
                messages.info(request, "You’ve already redeemed your joining kit. Below is your order summary.")
                return redirect('orders:summary')

            messages.error(request, "This email is already in use. Please login.")
            return redirect('accounts:login')

        # ✅ Create user and assign OTP
        user = User.objects.create(email=email)
        otp = generate_otp()
        user.otp = otp
        user.save()

        request.session['email'] = email
        request.session['otp'] = otp

        # ✅ Assign or reuse unique code
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        if not code_obj:
            code_obj = UniqueCode.objects.filter(assigned_to__isnull=True, is_used=False).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()
            else:
                return render(request, 'accounts/link_expired.html', {
                    'email': email,
                    'error': 'No redemption codes available at the moment.'
                })

        # ✅ Send welcome + OTP + code mail
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
