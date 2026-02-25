# ecommerce/urls.py - Complete URL configuration
from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    # Cart management
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout and payment
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # User purchases
    path('my-purchases/', views.my_purchases, name='my_purchases'),
    path('download/<int:item_id>/', views.download_item, name='download_item'),
    path('marketplace/', views.marketplace, name='marketplace'),
]
