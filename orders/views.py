"""
Views for comprehensive e-commerce order management.
"""
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import json
import logging

from blog.models import Post
from courses.models import Course, CourseEnrollment
from services.models import Service

from .models import Order, OrderItem, BasketItem, Invoice
from .email_service import OrderEmailService
from .crypto_service import coinbase_service, crypto_direct_service
from .utils import (
    ensure_course_enrollment,
    user_has_course_access,
    user_has_post_access,
    user_has_service_order,
)

logger = logging.getLogger(__name__)


# === CART MANAGEMENT ===

@csrf_exempt
def add_to_cart(request):
    """Add a product to the user's cart/basket."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    data = json.loads(request.body)
    product_type = data.get('product_type')
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if not product_type or not product_id:
        return JsonResponse({'success': False, 'error': 'Missing product information'})
    
    # Get or resolve the product
    product = None
    if product_type == 'post':
        product = get_object_or_404(Post, id=product_id, is_published=True)
    elif product_type == 'course':
        product = get_object_or_404(Course, id=product_id, is_published=True)
    elif product_type == 'service':
        product = get_object_or_404(Service, id=product_id, is_active=True)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid product type'})
    
    # Check if user already owns this product
    if has_user_purchased_product(request.user, product_type, product.id):
        return JsonResponse({'success': False, 'error': 'You already own this product'})
    
    # Check if it's free content
    if getattr(product, 'is_free', False):
        return JsonResponse({'success': False, 'error': 'This content is free'})
    
    # Check if item is already in basket
    basket_kwargs = {
        'user': request.user,
        product_type: product
    }
    
    basket_item, created = BasketItem.objects.get_or_create(
        defaults={'quantity': quantity},
        **basket_kwargs
    )
    
    if not created:
        # Update quantity if item already exists
        basket_item.quantity += quantity
        basket_item.save()
        action = 'updated'
    else:
        action = 'added'
    
    # Get basket count for response
    basket_count = BasketItem.objects.filter(user=request.user).count()
    
    return JsonResponse({
        'success': True, 
        'message': f'{product} {action} in cart',
        'basket_count': basket_count
    })


@csrf_exempt
@require_POST
def update_cart_item(request):
    """Update quantity of item in cart."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = int(data.get('quantity', 1))
    
    if not item_id or quantity < 1:
        return JsonResponse({'success': False, 'error': 'Invalid data'})
    
    try:
        basket_item = BasketItem.objects.get(id=item_id, user=request.user)
        basket_item.quantity = quantity
        basket_item.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Cart updated',
            'new_subtotal': float(basket_item.get_total_price()),
        })
    except BasketItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


@csrf_exempt
@require_POST
def remove_from_cart(request):
    """Remove a product from the user's cart."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    data = json.loads(request.body)
    item_id = data.get('item_id')
    
    if not item_id:
        return JsonResponse({'success': False, 'error': 'Missing item ID'})
    
    try:
        basket_item = BasketItem.objects.get(id=item_id, user=request.user)
        product_name = str(basket_item.get_product())
        basket_item.delete()
        
        # Get updated basket count
        basket_count = BasketItem.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True, 
            'message': f'{product_name} removed from cart',
            'basket_count': basket_count
        })
    except BasketItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


@login_required
def cart_view(request):
    """Display the user's shopping cart."""
    basket_items = BasketItem.objects.filter(user=request.user).select_related('post', 'course', 'service')
    
    # Calculate totals
    subtotal = sum(item.get_total_price() for item in basket_items)
    tax_amount = Decimal('0.00')  # No tax for now
    discount_amount = Decimal('0.00')  # No discounts for now
    total_amount = subtotal - discount_amount + tax_amount
    
    context = {
        'basket_items': basket_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
    }
    
    return render(request, 'orders/cart.html', context)


# === CHECKOUT PROCESS ===

@login_required
def checkout(request):
    """Checkout process - collect billing info and create pending order."""
    basket_items = BasketItem.objects.filter(user=request.user).select_related('post', 'course', 'service')
    
    if not basket_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('orders:cart')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get billing information
                billing_name = request.POST.get('billing_name', '').strip()
                billing_email = request.POST.get('billing_email', '').strip()
                billing_address = request.POST.get('billing_address', '').strip()
                
                if not billing_name or not billing_email:
                    messages.error(request, "Name and email are required.")
                    return render(request, 'orders/checkout.html', {
                        'basket_items': basket_items,
                        'subtotal': sum(item.get_total_price() for item in basket_items),
                        'total_amount': sum(item.get_total_price() for item in basket_items),
                        'billing_name': request.user.get_full_name(),
                        'billing_email': request.user.email,
                    })
                
                # Calculate totals
                subtotal = sum(item.get_total_price() for item in basket_items)
                tax_amount = Decimal('0.00')
                discount_amount = Decimal('0.00')
                total_amount = subtotal - discount_amount + tax_amount
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    billing_name=billing_name,
                    billing_email=billing_email,
                    billing_address=billing_address,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    discount_amount=discount_amount,
                    total_amount=total_amount,
                    status=Order.STATUS_PENDING
                )
                
                # Create order items with price snapshots
                for basket_item in basket_items:
                    product = basket_item.get_product()
                    OrderItem.objects.create(
                        order=order,
                        product_name=str(product),
                        product_type=basket_item.get_product_type(),
                        unit_price=basket_item.get_unit_price(),
                        quantity=basket_item.quantity,
                        **{basket_item.get_product_type(): product}
                    )
                
                return redirect('orders:payment', order_number=order.order_number)
                
        except Exception as e:
            logger.error(f"Checkout error for user {request.user}: {str(e)}")
            messages.error(request, "An error occurred during checkout. Please try again.")
    
    # GET request - show checkout form
    subtotal = sum(item.get_total_price() for item in basket_items)
    tax_amount = Decimal('0.00')
    total_amount = subtotal + tax_amount
    
    context = {
        'basket_items': basket_items,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'billing_name': request.user.get_full_name(),
        'billing_email': request.user.email,
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def payment_view(request, order_number):
    """Payment processing view."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.status == Order.STATUS_PAID:
        messages.info(request, "This order has already been paid.")
        return redirect('orders:order_confirmation', order_number=order.order_number)
    elif order.status not in [Order.STATUS_PENDING, Order.STATUS_FAILED]:
        messages.info(request, "This order cannot be processed.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                payment_method = request.POST.get('payment_method', 'demo')
                
                if payment_method == 'coinbase_commerce':
                    # Create Coinbase Commerce charge
                    charge = coinbase_service.create_charge(order)
                    
                    if 'error' in charge:
                        messages.error(request, f"Crypto payment error: {charge['error']}")
                        return render(request, 'orders/payment.html', {'order': order})
                    
                    # Save charge info to order
                    order.coinbase_charge_id = charge['id']
                    order.coinbase_hosted_url = charge['hosted_url']
                    order.payment_method = 'coinbase_commerce'
                    order.save(update_fields=['coinbase_charge_id', 'coinbase_hosted_url', 'payment_method', 'updated_at'])
                    
                    # Redirect to Coinbase Commerce checkout
                    return redirect(charge['hosted_url'])
                
                elif payment_method == 'crypto_direct':
                    # Direct crypto payment
                    crypto_currency = request.POST.get('crypto_currency', 'BTC')
                    payment_details = crypto_direct_service.generate_payment_address(crypto_currency, order)
                    
                    if 'error' in payment_details:
                        messages.error(request, f"Crypto payment error: {payment_details['error']}")
                        return render(request, 'orders/payment.html', {'order': order})
                    
                    # Save crypto payment info
                    order.payment_method = f'crypto_direct_{crypto_currency}'
                    order.crypto_currency = crypto_currency
                    order.crypto_address = payment_details['address']
                    order.crypto_amount = payment_details['amount_needed']
                    order.save(update_fields=['payment_method', 'crypto_currency', 'crypto_address', 'crypto_amount', 'updated_at'])
                    
                    # Redirect to crypto payment page
                    return redirect('orders:crypto_payment', order_number=order.order_number)
                
                else:
                    # Demo payment or traditional payment methods
                    # Mark order as paid for demo
                    order.mark_paid(
                        payment_method=payment_method,
                        transaction_id=f"demo_txn_{order.order_number}",
                        payment_amount=order.total_amount
                    )
                    
                    # Grant access to purchased products
                    order.grant_access_to_products()
                    
                    # Also grant access through OrderItems for content unlocking
                    for item in order.items.all():
                        if item.course:
                            ensure_course_enrollment(request.user, item.course)
                        # Post access is handled through order checking in utils
                    
                    # Clear cart
                    BasketItem.objects.filter(user=request.user).delete()
                    
                    # Send confirmation email
                    OrderEmailService.send_order_confirmation(order)
                    
                    # Update profile counters
                    profile = getattr(request.user, 'profile', None)
                    if profile:
                        profile.orders_count = Order.objects.filter(user=request.user, status=Order.STATUS_PAID).count()
                        profile.active_courses_count = CourseEnrollment.objects.filter(user=request.user).count()
                        profile.save(update_fields=['orders_count', 'active_courses_count'])
                    
                    messages.success(request, f"Payment successful! Order {order.order_number} has been confirmed.")
                    return redirect('orders:order_confirmation', order_number=order.order_number)
                
        except Exception as e:
            logger.error(f"Payment processing error for order {order.order_number}: {str(e)}")
            order.status = Order.STATUS_FAILED
            order.save(update_fields=['status', 'updated_at'])
            
            # Send payment failed email
            OrderEmailService.send_payment_failed(order)
            
            messages.error(request, "Payment processing failed. Please try again.")
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/payment.html', context)


@login_required
def order_confirmation(request, order_number):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def crypto_payment(request, order_number):
    """Direct crypto payment page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.status == Order.STATUS_PAID:
        messages.info(request, "This order has already been paid.")
        return redirect('orders:order_confirmation', order_number=order.order_number)
    
    if not order.crypto_address or not order.crypto_currency:
        messages.error(request, "Crypto payment not initialized.")
        return redirect('orders:payment', order_number=order.order_number)
    
    # Check payment status
    payment_status = crypto_direct_service.check_payment_status(
        order.crypto_address,
        order.crypto_currency,
        Decimal(order.crypto_amount or '0')
    )
    
    context = {
        'order': order,
        'payment_status': payment_status,
        'qr_code_url': f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={order.crypto_address}",
    }
    
    return render(request, 'orders/crypto_payment.html', context)


@login_required
def crypto_return(request, order_number):
    """Handle return from Coinbase Commerce."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    if order.coinbase_charge_id:
        # Get charge details from Coinbase Commerce
        charge = coinbase_service.get_charge(order.coinbase_charge_id)
        
        if charge and charge.get('payments'):
            # Check if payment was completed
            for payment in charge['payments']:
                if payment['status'] == 'CONFIRMED':
                    # Mark order as paid
                    order.mark_paid(
                        payment_method='coinbase_commerce',
                        transaction_id=payment['transaction_id'],
                        payment_amount=order.total_amount
                    )
                    
                    # Grant access and cleanup
                    order.grant_access_to_products()
                    for item in order.items.all():
                        if item.course:
                            ensure_course_enrollment(request.user, item.course)
                    
                    BasketItem.objects.filter(user=request.user).delete()
                    OrderEmailService.send_order_confirmation(order)
                    
                    messages.success(request, "Crypto payment confirmed! Your order has been completed.")
                    return redirect('orders:order_confirmation', order_number=order.order_number)
        
        # Payment not yet confirmed
        messages.info(request, "Your crypto payment is being processed. Please wait for confirmation.")
        return render(request, 'orders/crypto_pending.html', {'order': order})
    
    messages.error(request, "No crypto payment found for this order.")
    return redirect('orders:payment', order_number=order.order_number)


@csrf_exempt
def coinbase_webhook(request):
    """Handle Coinbase Commerce webhooks."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('X-CC-Webhook-Signature', '')
        
        if not coinbase_service.verify_webhook_signature(payload, signature):
            logger.warning("Invalid Coinbase Commerce webhook signature")
            return HttpResponse(status=400)
        
        event_data = json.loads(payload)
        event_type = event_data.get('event', {}).get('type')
        charge_data = event_data.get('event', {}).get('data', {})
        
        if event_type == 'charge:confirmed':
            # Payment confirmed
            charge_id = charge_data.get('id')
            metadata = charge_data.get('metadata', {})
            order_number = metadata.get('order_number')
            
            if order_number:
                try:
                    order = Order.objects.get(order_number=order_number, coinbase_charge_id=charge_id)
                    
                    if order.status != Order.STATUS_PAID:
                        # Get payment details
                        payments = charge_data.get('payments', [])
                        if payments:
                            payment = payments[0]  # Use first payment
                            transaction_id = payment.get('transaction_id', charge_id)
                            
                            order.mark_paid(
                                payment_method='coinbase_commerce',
                                transaction_id=transaction_id,
                                payment_amount=order.total_amount
                            )
                            
                            # Grant access
                            order.grant_access_to_products()
                            for item in order.items.all():
                                if item.course:
                                    ensure_course_enrollment(order.user, item.course)
                            
                            # Clear user's cart
                            BasketItem.objects.filter(user=order.user).delete()
                            
                            # Send confirmation email
                            OrderEmailService.send_order_confirmation(order)
                            
                            logger.info(f"Coinbase Commerce payment confirmed for order {order_number}")
                
                except Order.DoesNotExist:
                    logger.error(f"Order not found for Coinbase charge {charge_id}")
        
        elif event_type == 'charge:failed':
            # Payment failed
            charge_id = charge_data.get('id')
            metadata = charge_data.get('metadata', {})
            order_number = metadata.get('order_number')
            
            if order_number:
                try:
                    order = Order.objects.get(order_number=order_number, coinbase_charge_id=charge_id)
                    order.status = Order.STATUS_FAILED
                    order.save(update_fields=['status', 'updated_at'])
                    
                    OrderEmailService.send_payment_failed(order)
                    logger.info(f"Coinbase Commerce payment failed for order {order_number}")
                
                except Order.DoesNotExist:
                    logger.error(f"Order not found for failed Coinbase charge {charge_id}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Coinbase webhook error: {str(e)}")
        return HttpResponse(status=500)


# === INVOICE MANAGEMENT ===

@login_required
def invoice_view(request, invoice_number):
    """View/download invoice."""
    invoice = get_object_or_404(Invoice, invoice_number=invoice_number, order__user=request.user)
    
    if request.GET.get('download') == 'pdf':
        # Generate PDF (placeholder for now)
        return HttpResponse("PDF generation not implemented yet", content_type="text/plain")
    
    context = {
        'invoice': invoice,
        'order': invoice.order,
    }
    
    return render(request, 'orders/invoice.html', context)


# === UTILITY FUNCTIONS ===

def has_user_purchased_product(user, product_type, product_id):
    """Check if user has purchased a specific product."""
    # Check legacy order structure
    legacy_check = Order.objects.filter(
        user=user,
        status=Order.STATUS_PAID,
        **{product_type: product_id}
    ).exists()
    
    if legacy_check:
        return True
    
    # Check new OrderItem structure
    return Order.objects.filter(
        user=user,
        status=Order.STATUS_PAID,
        items__isnull=False
    ).filter(**{f'items__{product_type}__id': product_id}).exists()


# === LEGACY SUPPORT & COMPATIBILITY ===

def _resolve_product(params):
    """Return (product_type, product_object). Legacy function for backward compatibility."""
    post_slug = params.get('post')
    course_slug = params.get('course')
    service_slug = params.get('service')

    if post_slug:
        post = get_object_or_404(Post, slug=post_slug, is_published=True)
        return 'post', post
    if course_slug:
        course = get_object_or_404(Course, slug=course_slug, is_published=True)
        return 'course', course
    if service_slug:
        service = get_object_or_404(Service, slug=service_slug, is_active=True)
        return 'service', service
    raise Http404("No purchasable item specified.")


def _get_price(product_type, product):
    """Get product price. Legacy function for backward compatibility."""
    if product_type == 'post':
        return Decimal(product.price or 0)
    if product_type == 'course':
        return Decimal(product.price or 0)
    if product_type == 'service':
        return Decimal(product.fixed_price or product.starting_price or 0)
    return Decimal('0.00')


def _get_success_url(product_type, product):
    """Get success URL after purchase. Legacy function for backward compatibility."""
    if product_type == 'post':
        return product.get_absolute_url()
    if product_type == 'course':
        first_lesson = product.lessons.filter(is_published=True).order_by('order', 'created_at').first()
        return first_lesson.get_absolute_url() if first_lesson else product.get_absolute_url()
    if product_type == 'service':
        return product.get_absolute_url()
    return reverse('core:home')


@login_required
def create_order(request):
    """Legacy single-product order creation for backward compatibility."""
    product_type, product = _resolve_product(request.GET if request.method == 'GET' else request.POST)
    price = _get_price(product_type, product)
    success_url = _get_success_url(product_type, product)

    # Short-circuit for free content
    if product_type == 'post' and getattr(product, 'is_free', False):
        messages.info(request, 'This tutorial is free to read.')
        return redirect(product.get_absolute_url())
    if product_type == 'course' and getattr(product, 'is_free', False):
        ensure_course_enrollment(request.user, product)
        messages.success(request, 'You are enrolled. Enjoy the course!')
        return redirect(success_url)

    # Prevent duplicate purchases
    if has_user_purchased_product(request.user, product_type, product.id):
        messages.info(request, f'You already own this {product_type}.')
        return redirect(success_url)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create order with new structure
                order = Order.objects.create(
                    user=request.user,
                    billing_name=request.user.get_full_name() or request.user.email,
                    billing_email=request.user.email,
                    subtotal=price,
                    total_amount=price,
                    status=Order.STATUS_PENDING,
                    # Legacy fields for backward compatibility
                    product_type=product_type,
                    amount=price,
                    **{product_type: product}
                )
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product_name=str(product),
                    product_type=product_type,
                    unit_price=price,
                    quantity=1,
                    **{product_type: product}
                )
                
                # Mark as paid (simulated payment)
                order.mark_paid()
                order.grant_access_to_products()
                
                # Update profile counters
                profile = getattr(request.user, 'profile', None)
                if profile:
                    if product_type == 'course':
                        profile.active_courses_count = CourseEnrollment.objects.filter(user=request.user).count()
                    profile.orders_count = Order.objects.filter(user=request.user, status=Order.STATUS_PAID).count()
                    profile.save(update_fields=['orders_count', 'active_courses_count'] if product_type == 'course' else ['orders_count'])

                messages.success(request, 'Payment successful. Access unlocked!')
                return redirect(success_url)
        except Exception as e:
            logger.error(f"Legacy order creation error: {str(e)}")
            messages.error(request, "An error occurred. Please try again.")

    context = {
        'product': product,
        'product_type': product_type,
        'price': price,
    }
    return render(request, 'orders/legacy_checkout.html', context)


@login_required
@require_POST
def add_to_basket(request):
    """Legacy add to basket function. Redirects to new cart system."""
    product_type, product = _resolve_product(request.POST)
    
    # Check if item is already owned
    if has_user_purchased_product(request.user, product_type, product.id):
        messages.info(request, f'You already own this {product_type}.')
        return redirect(product.get_absolute_url())
    
    # Short-circuit for free content
    if getattr(product, 'is_free', False):
        messages.info(request, f'This {product_type} is free.')
        if product_type == 'course':
            ensure_course_enrollment(request.user, product)
            messages.success(request, 'You are enrolled. Enjoy the course!')
        return redirect(product.get_absolute_url())
    
    # Add to basket using new system
    basket_kwargs = {
        'user': request.user,
        product_type: product
    }
    
    try:
        basket_item, created = BasketItem.objects.get_or_create(
            defaults={'quantity': 1},
            **basket_kwargs,
        )
        if not created:
            basket_item.quantity += 1
            basket_item.save()
            messages.success(request, f'Updated quantity for {product}')
        else:
            messages.success(request, f'Added {product} to your cart')
    except IntegrityError:
        messages.info(request, 'Item is already in your cart')
    
    return redirect('orders:cart')


@login_required
def view_basket(request):
    """Legacy basket view. Redirects to new cart view."""
    return redirect('orders:cart')


@login_required
@require_POST  
def update_basket_item(request, item_id):
    """Legacy basket item update function."""
    basket_item = get_object_or_404(BasketItem, id=item_id, user=request.user)
    
    action = request.POST.get('action')
    if action == 'increase':
        basket_item.quantity += 1
        basket_item.save()
    elif action == 'decrease':
        if basket_item.quantity > 1:
            basket_item.quantity -= 1
            basket_item.save()
        else:
            basket_item.delete()
            messages.success(request, 'Item removed from cart')
            return redirect('orders:cart')
    elif action == 'remove':
        basket_item.delete()
        messages.success(request, 'Item removed from cart')
        return redirect('orders:cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'quantity': basket_item.quantity,
            'total_price': str(basket_item.get_total_price()),
            'basket_total': str(sum(item.get_total_price() for item in BasketItem.objects.filter(user=request.user)))
        })
    
    return redirect('orders:cart')


@login_required
def checkout_basket(request):
    """Legacy basket checkout. Redirects to new checkout process."""
    basket_items = BasketItem.objects.filter(user=request.user)
    
    if not basket_items.exists():
        messages.info(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    # For legacy support, we'll redirect to the new checkout flow
    return redirect('orders:checkout')


# === ALIASES FOR BACKWARD COMPATIBILITY ===

# Alias the new functions with legacy names
basket_view = cart_view
remove_from_basket = remove_from_cart