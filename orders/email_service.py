"""
Email service for order notifications.
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class OrderEmailService:
    """Service for sending order-related emails."""
    
    @staticmethod
    def send_order_confirmation(order):
        """Send order confirmation email after successful payment."""
        try:
            subject = f"Order Confirmation - {order.order_number}"
            
            # Render HTML email
            html_content = render_to_string('orders/emails/order_confirmation.html', {
                'order': order,
                'site_name': 'AMStack',
                'dashboard_url': f"{settings.SITE_URL}/accounts/dashboard/",
                'invoice_url': f"{settings.SITE_URL}/orders/invoice/{order.invoice.invoice_number}/" if hasattr(order, 'invoice') else None,
            })
            
            # Create plain text version
            text_content = strip_tags(html_content)
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.billing_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"Order confirmation email sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation email for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_failed(order):
        """Send payment failed email."""
        try:
            subject = f"Payment Failed - Order {order.order_number}"
            
            html_content = render_to_string('orders/emails/payment_failed.html', {
                'order': order,
                'site_name': 'AMStack',
                'retry_url': f"{settings.SITE_URL}/orders/retry-payment/{order.order_number}/",
            })
            
            text_content = strip_tags(html_content)
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.billing_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"Payment failed email sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment failed email for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def send_refund_notification(order):
        """Send refund notification email."""
        try:
            subject = f"Refund Processed - Order {order.order_number}"
            
            html_content = render_to_string('orders/emails/refund_notification.html', {
                'order': order,
                'site_name': 'AMStack',
                'support_email': settings.DEFAULT_FROM_EMAIL,
            })
            
            text_content = strip_tags(html_content)
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.billing_email],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"Refund notification email sent for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send refund notification email for order {order.order_number}: {str(e)}")
            return False