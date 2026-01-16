from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # New E-commerce Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout Flow
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<str:order_number>/', views.payment_view, name='payment'),
    path('confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    
    # Invoice Management
    path('invoice/<str:invoice_number>/', views.invoice_view, name='invoice'),
    
    # Legacy URLs for backward compatibility
    path('create/', views.create_order, name='create_order'),
    path('basket/add/', views.add_to_basket, name='add_to_basket'),
    path('basket/', views.view_basket, name='view_basket'),
    path('basket/update/<int:item_id>/', views.update_basket_item, name='update_basket_item'),
    path('basket/checkout/', views.checkout_basket, name='checkout_basket'),
]
