#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from orders.models import Order

legacy_order = Order.objects.exclude(reference='').exclude(reference__isnull=True).first()
if legacy_order:
    print(f'Legacy Order:')
    print(f'  Reference: "{legacy_order.reference}"')
    print(f'  Amount (legacy): ${legacy_order.amount}')
    print(f'  Total Amount: ${legacy_order.total_amount}')
    print(f'  Display Amount: ${legacy_order.get_display_amount()}')