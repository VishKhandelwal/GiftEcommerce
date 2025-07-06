from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
]
