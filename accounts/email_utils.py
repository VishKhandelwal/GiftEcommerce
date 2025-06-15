from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_gift_link_email(user_email):
    subject = "Your Gift Link is Here!"
    link = "http://127.0.0.1:8000/t/giftbox/"  # Same link for everyone

    html_content = render_to_string("emails/gift_link.html", {
        "link": link,
        "email": user_email
    })
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, "your@from.email", [user_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
