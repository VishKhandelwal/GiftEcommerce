from django.urls import path
from . import views

app_name = 'admin_dashboard'  # This is what defines the namespace


urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),  # ✅ THIS LINE FIXES THE ERROR
    path('logout/', views.admin_logout, name='admin_logout'),
]
