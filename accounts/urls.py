from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify/', views.verify_otp, name='verify'),
    path('resend_otp/',  views.resend_otp, name='resend_otp'),
    path('logout/', views.logout_view, name='logout'),
]
