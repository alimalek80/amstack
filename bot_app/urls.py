"""
URL configuration for bot_app
"""
from django.urls import path
from . import views

app_name = 'bot_app'

urlpatterns = [
    # Telegram webhook endpoint
    # The actual path should include a secret token for security
    # Example: /bot/webhook/{SECRET_TOKEN}/
    path('webhook/<str:token>/', views.telegram_webhook, name='telegram_webhook'),
    
    # Webhook info endpoint (for debugging)
    path('webhook-info/', views.webhook_info, name='webhook_info'),
]
