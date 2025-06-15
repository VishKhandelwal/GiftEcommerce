from django.core.mail import send_mail



def send_otp_email(email, otp):
    subject = "Your Order Tracking OTP"
    message = "Your OTP for tracking the order is: {otp}"
    from_email = "your_email@example.com"  # use configured sender
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
