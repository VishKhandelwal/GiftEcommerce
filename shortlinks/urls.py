from django.urls import path
from .views import redirect_short_url

urlpatterns = [
    path('<str:code>/', redirect_short_url, name='redirect_short_url'),
]
