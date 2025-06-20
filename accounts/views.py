from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
import random
from accounts.models import UniqueCode
from .otp_utils import send_otp
from django.template.loader import render_to_string
from datetime import timedelta
import random


User = get_user_model()
from accounts.models import CustomUser as User, UniqueCode



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = str(random.randint(100000, 999999))

        # Get or create the user
        user, _ = User.objects.get_or_create(email=email)
        user.otp = otp
        user.save()

        # Store OTP and email in session
        request.session['otp'] = otp
        request.session['email'] = email

        # Step 1: Check if a code is already assigned and not expired
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        if code_obj and code_obj.assigned_time:
            expiry_time = code_obj.assigned_time + timedelta(days=7)
            if timezone.now() > expiry_time:
                code_obj.is_used = True
                code_obj.save()
                code_obj = None  # Expired, so nullify

        # Step 2: Try to reuse an expired assigned code (for the same user)
        if not code_obj:
            code_obj = UniqueCode.objects.filter(
                assigned_to=email,
                is_used=False,
                assigned_time__lt=timezone.now() - timedelta(days=7)
            ).first()

        # Step 3: Try to assign a completely fresh unused, unassigned code
        if not code_obj:
            code_obj = UniqueCode.objects.filter(
                assigned_to__isnull=True,
                is_used=False
            ).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Prepare email context
        context = {
            'otp': otp,
            'unique_code': code_obj.code if code_obj else None,
        }

        # Load templates
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)

        # Send email
        send_mail(
            subject="🎁 Redeem Your Gift Hamper - Team Infinity",
            message=plain_message,
            from_email="hello@theinfinitybox.in",
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )

        return render(request, 'accounts/verify.html', {'email': email})

    return render(request, 'accounts/login.html')



# Step 2: Verify OTP
User = get_user_model()

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
            return redirect("products:choose_box")
        else:
            return render(request, "accounts/verify.html", {
                "email": email,
                "error": "Invalid OTP"
            })

    return render(request, "accounts/verify.html")

# Step 3: Logout
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
