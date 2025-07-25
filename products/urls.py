from django.urls import path
from .cart import view_cart, add_to_cart
from .checkout import checkout_view
from . import views


app_name = 'products'


urlpatterns = [
    path('custombox/choose_box/', views.choose_box, name='choose_box'),
    path('custombox/choose_items/', views.choose_items, name='choose_items'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('', views.cart_view, name='view_cart'),
    path('cart-summary/', views.cart_summary_ajax, name='cart_summary_ajax'),
    path('custombox/magic_created/', views.magic_created, name='magic_created'),
    path('cart/', view_cart, name='cart'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('order-preview/', views.order_preview, name='order_preview'),


]
    


