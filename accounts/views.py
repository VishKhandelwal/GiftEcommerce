from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
import random

from accounts.models import CustomUser as User, UniqueCode
from .otp_utils import send_otp
from .email_utils import send_gift_link_email



User = get_user_model()
from accounts.models import CustomUser as User, UniqueCode


def send_otp_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        # Send OTP logic
        otp = str(random.randint(100000, 999999))
        user, _ = User.objects.get_or_create(email=email)
        user.otp = otp
        user.save()

        request.session['otp'] = otp
        request.session['email'] = email

        # Assign or fetch unique code (optional)
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()
        if not code_obj:
            code_obj = UniqueCode.objects.filter(is_used=False, assigned_to__isnull=True).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Send OTP + Code by plain email
        message = f"Your OTP is: {otp}"
        if code_obj:
            message += f"\nYour Unique Code: {code_obj.code}"
        else:
            message += "\n(No unique code available)"

        send_mail(
            subject="Your Login OTP and Unique Code",
            message=message,
            from_email="GiftBox <vaishali.kh2310@gmail.com>",
            recipient_list=[email],
            fail_silently=False,
        )

        # ✅ Send gift link email with fixed link
        send_gift_link_email(user={"email": email})

        return redirect("login_view")

    return render(request, 'accounts/login.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = str(random.randint(100000, 999999))

        # Get or create the user
        user, _ = User.objects.get_or_create(email=email)
        user.otp = otp  # Only if CustomUser has an `otp` field. Otherwise store in session.
        user.save()

        # Store OTP and email in session
        request.session['otp'] = otp
        request.session['email'] = email

        # Assign or fetch existing unique code
        code_obj = UniqueCode.objects.filter(assigned_to=email, is_used=False).first()

        if not code_obj:
            # Try to assign a fresh unused and unassigned code
            code_obj = UniqueCode.objects.filter(is_used=False, assigned_to__isnull=True).first()
            if code_obj:
                code_obj.assigned_to = email
                code_obj.assigned_time = timezone.now()
                code_obj.save()

        # Build email message
        message = f"Your OTP is: {otp}"
        if code_obj:
            message += f"\nYour Unique Code: {code_obj.code}"
        else:
            message += "\n(Note: No Unique Code available currently)"

        # Send email
        send_mail(
            subject="Your Login OTP and Unique Code",
            message=message,
            from_email="GiftBox <vaishali.kh2310@gmail.com>",
            recipient_list=[email],
            fail_silently=False,
        )

        return render(request, 'accounts/verify.html', {'email': email})

    return render(request, 'accounts/login.html')


# Step 2: Verify OTP
def verify_otp(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")
        email = request.session.get("email")

        if input_otp == session_otp and email:
            user, _ = User.objects.get_or_create(email=email)
            login(request, user)
            return redirect("products:choose_box")  # Redirect after successful login
        else:
            messages.error(request, "Invalid OTP")

    return render(request, "accounts/verify.html")  # Re-render on error or GET

def resend_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            send_otp(email)
            return redirect('accounts:login')
    return redirect('accounts:login')

# Step 3: Logout
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
