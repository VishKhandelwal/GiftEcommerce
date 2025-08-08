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
from django.contrib.auth import get_user_model
from .otp_utils import generate_otp, send_otp
from orders.models import Order
from .models import UniqueCode
from accounts.models import CustomUser as User, UniqueCode


# Utility: OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))

User = get_user_model()


from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from orders.models import Order

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import login

from .models import User, UniqueCode
from orders.models import Order
from .utils import generate_otp  # Your OTP generator

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_entered = request.POST.get('otp')

        # Step 1: If OTP is entered, verify it
        if otp_entered:
            session_email = request.session.get('email')
            session_otp = request.session.get('otp')

            if not session_email or otp_entered != session_otp:
                messages.error(request, "Invalid or expired OTP.")
                return redirect('accounts:login')

            user = User.objects.filter(email=session_email).first()
            if not user:
                messages.error(request, "User not found.")
                return redirect('accounts:login')

            login(request, user)
            return redirect('orders:summary')

        # Step 2: If only email is entered, start login process
        if not email:
            messages.error(request, "Email is required.")
            return redirect('accounts:login')

        user = User.objects.filter(email=email).first()

        # Existing user with order → go to summary
        if user and Order.objects.filter(user=user).exists():
            login(request, user)
            return redirect('orders:summary')

        # If user doesn't exist, create one
        if not user:
            user = User.objects.create(email=email)

        # Generate and store OTP in session
        otp = generate_otp()
        request.session['email'] = email
        request.session['otp'] = otp

        # Assign unique code if needed
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()
        if not code_obj:
            code_obj = UniqueCode.objects.filter(assigned_to__isnull=True, is_used=False).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Send OTP email
        context = {
            'otp': otp,
            'unique_code': code_obj.code if code_obj else None,
        }
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)

        send_mail(
            subject="🔑 Your OTP - Team Infinity",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
        )

        messages.info(request, "OTP sent to your email. Please enter it below.")
        return render(request, 'accounts/login.html', {'email': email, 'otp_sent': True})

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
    email = request.session.get("email")
    session_otp = request.session.get("otp")
    next_url = request.POST.get("next") or request.session.get("next")

    if request.method == "POST":
        input_otp = request.POST.get("otp")
        agreed = request.POST.get("agree_terms")

        # ✅ Resend OTP
        if request.POST.get("resend_otp"):
            new_otp = send_otp(email)
            request.session['otp'] = new_otp
            return render(request, "accounts/verify.html", {
                "email": email,
                "success": "OTP resent successfully.",
                "next": next_url,
            })

        # ✅ Data policy must be agreed
        if not agreed:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": "Please agree to the data policy.",
                "next": next_url,
            })

        # ✅ OTP match check
        if input_otp == session_otp and email:
            user, _ = User.objects.get_or_create(email=email)
            login(request, user)

            # ✅ Check for existing order
            if Order.objects.filter(user=user).exists():
                return redirect("orders:summary")

            # ✅ Safe redirect to next URL or default
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            return redirect("products:choose_box")

        return render(request, "accounts/verify.html", {
            "email": email,
            "error": "Invalid OTP",
            "next": next_url,
        })

    # ✅ GET request fallback
    return render(request, "accounts/verify.html", {
        "email": email,
        "next": next_url or "",
    })


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
