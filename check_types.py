#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from orders.models import Order

orders = Order.objects.filter(status='paid').order_by('-created_at')
print('CHECKING PRODUCT TYPES:')
for order in orders:
    print(f'Order {order.order_number or order.reference}:')
    print(f'  product_type: "{order.product_type}"')
    print(f'  Legacy fields: post={bool(order.post)}, course={bool(order.course)}, service={bool(order.service)}')
    if order.items.exists():
        item = order.items.first()
        print(f'  First item: post={bool(item.post)}, course={bool(item.course)}, service={bool(item.service)}')
        print(f'  Item product_type: "{item.product_type}"')
    print('---')