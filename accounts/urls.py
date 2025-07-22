from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # urls.py
    path('', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('new_user/', views.new_user, name='new_user'),
    path('verify/', views.verify_otp, name='verify'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.logout_view, name='logout'),
]
