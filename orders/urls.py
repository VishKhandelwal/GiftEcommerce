from django.urls import path
from .views import track_order_view
from .views import my_orders_view

app_name = 'orders'

urlpatterns = [
    path('track/', track_order_view, name='track_order'),
    path('my/', my_orders_view, name='my_orders'),
    
]
