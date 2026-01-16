#!/usr/bin/env python
"""
Check order structure
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from orders.models import Order

orders = Order.objects.filter(status='paid').order_by('-created_at')
print('PAID ORDERS:')
for order in orders:
    print(f'Order Number: "{order.order_number}" | Reference: "{order.reference}" | Total: ${order.total_amount} | Items: {order.items.count()}')
    for item in order.items.all():
        print(f'  Item: {item.product_name} -> Post: {bool(item.post)} | Course: {bool(item.course)} | Service: {bool(item.service)}')
        if item.post:
            print(f'    Post URL: {item.post.get_absolute_url()}')
        if item.course:
            print(f'    Course URL: {item.course.get_absolute_url()}')