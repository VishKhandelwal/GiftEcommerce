from django.urls import path
from .views import admin_dashboard
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

