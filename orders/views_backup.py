from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from blog.models import Post
from courses.models import Course, CourseEnrollment
from services.models import Service

from .models import Order, BasketItem
from .utils import (
    ensure_course_enrollment,
    user_has_course_access,
    user_has_post_access,
    user_has_service_order,
)


def _resolve_product(params):
    """Return (product_type, product_object)."""
    post_slug = params.get('post')
    course_slug = params.get('course')
    service_slug = params.get('service')

    if post_slug:
        post = get_object_or_404(Post, slug=post_slug, is_published=True)
        return Order.PRODUCT_POST, post
    if course_slug:
        course = get_object_or_404(Course, slug=course_slug, is_published=True)
        return Order.PRODUCT_COURSE, course
    if service_slug:
        service = get_object_or_404(Service, slug=service_slug, is_active=True)
        return Order.PRODUCT_SERVICE, service
    raise Http404("No purchasable item specified.")


def _get_price(product_type, product):
    if product_type == Order.PRODUCT_POST:
        return Decimal(product.price or 0)
    if product_type == Order.PRODUCT_COURSE:
        return Decimal(product.price or 0)
    if product_type == Order.PRODUCT_SERVICE:
        return Decimal(product.fixed_price or product.starting_price or 0)
    return Decimal('0.00')


def _get_success_url(product_type, product):
    if product_type == Order.PRODUCT_POST:
        return product.get_absolute_url()
    if product_type == Order.PRODUCT_COURSE:
        first_lesson = product.lessons.filter(is_published=True).order_by('order', 'created_at').first()
        return first_lesson.get_absolute_url() if first_lesson else product.get_absolute_url()
    if product_type == Order.PRODUCT_SERVICE:
        return product.get_absolute_url()
    return reverse('core:home')


@login_required
def create_order(request):
    product_type, product = _resolve_product(request.GET if request.method == 'GET' else request.POST)
    price = _get_price(product_type, product)
    success_url = _get_success_url(product_type, product)

    # Short-circuit for free content
    if product_type == Order.PRODUCT_POST and product.is_free:
        messages.info(request, 'This tutorial is free to read.')
        return redirect(product.get_absolute_url())
    if product_type == Order.PRODUCT_COURSE and product.is_free:
        ensure_course_enrollment(request.user, product)
        messages.success(request, 'You are enrolled. Enjoy the course!')
        return redirect(success_url)

    # Prevent duplicate purchases
    if product_type == Order.PRODUCT_POST and user_has_post_access(request.user, product):
        messages.info(request, 'You already own this tutorial.')
        return redirect(success_url)
    if product_type == Order.PRODUCT_COURSE and user_has_course_access(request.user, product):
        messages.info(request, 'You already own this course.')
        return redirect(success_url)
    if product_type == Order.PRODUCT_SERVICE and user_has_service_order(request.user, product):
        messages.info(request, 'You already placed an order for this service.')
        return redirect(success_url)

    if request.method == 'POST':
        # Create or update the order, then mark as paid (simulated checkout)
        order_kwargs = {
            'user': request.user,
            'product_type': product_type,
            'post': product if product_type == Order.PRODUCT_POST else None,
            'course': product if product_type == Order.PRODUCT_COURSE else None,
            'service': product if product_type == Order.PRODUCT_SERVICE else None,
        }

        order, created = Order.objects.get_or_create(
            defaults={'amount': price},
            **order_kwargs,
        )

        if order.amount != price:
            order.amount = price
            order.save(update_fields=['amount', 'updated_at'])

        order.mark_paid()

        profile = getattr(request.user, 'profile', None)
        profile_fields = []

        if product_type == Order.PRODUCT_COURSE:
            ensure_course_enrollment(request.user, product)
            if profile:
                profile.active_courses_count = CourseEnrollment.objects.filter(user=request.user).count()
                profile_fields.append('active_courses_count')

        if profile:
            profile.orders_count = Order.objects.filter(user=request.user, status=Order.STATUS_PAID).count()
            profile_fields.append('orders_count')
            if profile_fields:
                profile.save(update_fields=profile_fields)

        messages.success(request, 'Payment successful. Access unlocked!')
        return redirect(success_url)

    context = {
        'product': product,
        'product_type': product_type,
        'price': price,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@require_POST
def add_to_basket(request):
    """Add an item to the user's basket."""
    product_type, product = _resolve_product(request.POST)
    
    # Check if item is already owned
    if product_type == Order.PRODUCT_POST and user_has_post_access(request.user, product):
        messages.info(request, 'You already own this tutorial.')
        return redirect(product.get_absolute_url())
    if product_type == Order.PRODUCT_COURSE and user_has_course_access(request.user, product):
        messages.info(request, 'You already own this course.')
        return redirect(product.get_absolute_url())
    if product_type == Order.PRODUCT_SERVICE and user_has_service_order(request.user, product):
        messages.info(request, 'You already placed an order for this service.')
        return redirect(product.get_absolute_url())
    
    # Short-circuit for free content
    if product_type == Order.PRODUCT_POST and product.is_free:
        messages.info(request, 'This tutorial is free to read.')
        return redirect(product.get_absolute_url())
    if product_type == Order.PRODUCT_COURSE and product.is_free:
        ensure_course_enrollment(request.user, product)
        messages.success(request, 'You are enrolled. Enjoy the course!')
        first_lesson = product.lessons.filter(is_published=True).order_by('order', 'created_at').first()
        return redirect(first_lesson.get_absolute_url() if first_lesson else product.get_absolute_url())
    
    # Add to basket
    basket_kwargs = {
        'user': request.user,
        'post': product if product_type == Order.PRODUCT_POST else None,
        'course': product if product_type == Order.PRODUCT_COURSE else None,
        'service': product if product_type == Order.PRODUCT_SERVICE else None,
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
            messages.success(request, f'Added {product} to your basket')
    except IntegrityError:
        messages.info(request, 'Item is already in your basket')
    
    return redirect('orders:view_basket')


@login_required
def view_basket(request):
    """Display the user's basket."""
    basket_items = BasketItem.objects.filter(user=request.user).select_related(
        'post', 'course', 'service'
    )
    
    total = sum(item.get_total_price() for item in basket_items)
    
    context = {
        'basket_items': basket_items,
        'total': total,
    }
    return render(request, 'orders/basket.html', context)


@login_required
@require_POST
def update_basket_item(request, item_id):
    """Update quantity of a basket item."""
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
            messages.success(request, 'Item removed from basket')
            return redirect('orders:view_basket')
    elif action == 'remove':
        basket_item.delete()
        messages.success(request, 'Item removed from basket')
        return redirect('orders:view_basket')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'quantity': basket_item.quantity,
            'total_price': str(basket_item.get_total_price()),
            'basket_total': str(sum(item.get_total_price() for item in BasketItem.objects.filter(user=request.user)))
        })
    
    return redirect('orders:view_basket')


@login_required
def checkout_basket(request):
    """Checkout all items in the basket."""
    basket_items = BasketItem.objects.filter(user=request.user).select_related(
        'post', 'course', 'service'
    )
    
    if not basket_items.exists():
        messages.info(request, 'Your basket is empty')
        return redirect('orders:view_basket')
    
    if request.method == 'POST':
        # Process each item in the basket
        total_amount = Decimal('0.00')
        orders_created = []
        
        for item in basket_items:
            product = item.get_product()
            product_type = item.get_product_type()
            unit_price = item.get_unit_price()
            
            for _ in range(item.quantity):
                order_kwargs = {
                    'user': request.user,
                    'product_type': product_type,
                    'post': product if product_type == Order.PRODUCT_POST else None,
                    'course': product if product_type == Order.PRODUCT_COURSE else None,
                    'service': product if product_type == Order.PRODUCT_SERVICE else None,
                }
                
                order, created = Order.objects.get_or_create(
                    defaults={'amount': unit_price},
                    **order_kwargs,
                )
                
                if order.amount != unit_price:
                    order.amount = unit_price
                    order.save(update_fields=['amount', 'updated_at'])
                
                order.mark_paid()
                orders_created.append(order)
                total_amount += unit_price
                
                # Enroll in courses
                if product_type == Order.PRODUCT_COURSE:
                    ensure_course_enrollment(request.user, product)
        
        # Clear basket
        basket_items.delete()
        
        # Update profile counters
        profile = getattr(request.user, 'profile', None)
        if profile:
            profile.orders_count = Order.objects.filter(user=request.user, status=Order.STATUS_PAID).count()
            profile.active_courses_count = CourseEnrollment.objects.filter(user=request.user).count()
            profile.save(update_fields=['orders_count', 'active_courses_count'])
        
        messages.success(request, f'Payment successful! {len(orders_created)} items purchased.')
        return redirect('accounts:dashboard')
    
    total = sum(item.get_total_price() for item in basket_items)
    
    context = {
        'basket_items': basket_items,
        'total': total,
    }
    return render(request, 'orders/checkout_basket.html', context)