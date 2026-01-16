#!/usr/bin/env python
"""
Script to check and fix order issues
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from orders.models import Order, OrderItem
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

def check_orders():
    print("=== ORDER STATUS CHECK ===")
    orders = Order.objects.all().order_by('-created_at')
    print(f'Total orders: {orders.count()}')
    
    for status in ['pending', 'paid', 'failed']:
        count = orders.filter(status=status).count()
        print(f'{status.upper()} orders: {count}')
    
    print("\n=== RECENT ORDERS ===")
    for order in orders[:10]:
        amount = order.total_amount or order.amount or Decimal('0.00')
        print(f'{order.order_number or "No-number"}: Status={order.status}, Amount=${amount}, Items={order.items.count()}')
        if order.items.exists():
            for item in order.items.all():
                print(f'  - {item.product_name}: ${item.unit_price} x {item.quantity}')


def cleanup_pending_orders():
    print("\n=== CLEANUP PENDING ORDERS ===")
    pending_orders = Order.objects.filter(status='pending')
    
    orders_to_delete = []
    for order in pending_orders:
        # Delete pending orders that are older than 1 hour or have no items
        from django.utils import timezone
        from datetime import timedelta
        
        is_old = order.created_at < timezone.now() - timedelta(hours=1)
        has_no_items = order.items.count() == 0
        has_no_amount = not (order.total_amount or order.amount)
        
        if is_old or has_no_items or has_no_amount:
            orders_to_delete.append(order.order_number or str(order.id))
            order.delete()
    
    print(f"Deleted {len(orders_to_delete)} pending orders: {orders_to_delete}")


def fix_order_amounts():
    print("\n=== FIX ORDER AMOUNTS ===")
    orders_without_total = Order.objects.filter(total_amount__isnull=True).exclude(status='pending')
    
    fixed_count = 0
    for order in orders_without_total:
        if order.amount:  # Legacy field has amount
            order.total_amount = order.amount
            order.subtotal = order.amount
            order.save(update_fields=['total_amount', 'subtotal'])
            fixed_count += 1
            print(f"Fixed order {order.order_number}: Set total_amount to ${order.amount}")
        elif order.items.exists():
            # Calculate from items
            order.calculate_totals()
            fixed_count += 1
            print(f"Fixed order {order.order_number}: Calculated total_amount to ${order.total_amount}")
    
    print(f"Fixed {fixed_count} orders with missing amounts")


if __name__ == '__main__':
    check_orders()
    cleanup_pending_orders()
    fix_order_amounts()
    print("\n=== AFTER CLEANUP ===")
    check_orders()