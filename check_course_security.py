#!/usr/bin/env python
"""
Check if users have unauthorized course enrollments
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from courses.models import Course, CourseEnrollment
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

def check_enrollments():
    print("🔍 CHECKING COURSE ENROLLMENTS AND PURCHASES")
    print("=" * 50)
    
    course = Course.objects.filter(slug='full-stack-react-django-masterclass').first()
    if not course:
        print("❌ Course not found")
        return
    
    print(f"📚 Course: {course.title}")
    print(f"💰 Price: ${course.price}")
    print(f"🔒 Is Free: {course.is_free}")
    print()
    
    # Check lessons
    lessons = course.lessons.filter(is_published=True).order_by('order')
    print("📖 LESSONS:")
    for lesson in lessons:
        status = "🆓 FREE" if lesson.is_free else "🔒 PAID"
        print(f"  {lesson.order}. {lesson.title} - {status}")
    print()
    
    # Check enrollments
    enrollments = CourseEnrollment.objects.filter(course=course)
    print(f"👥 ENROLLMENTS: {enrollments.count()}")
    
    for enrollment in enrollments:
        user = enrollment.user
        # Check if user has paid for this course
        has_paid = Order.objects.filter(
            user=user,
            course=course,
            status=Order.STATUS_PAID
        ).exists()
        
        # Check new order structure
        has_paid_new = Order.objects.filter(
            user=user,
            status=Order.STATUS_PAID,
            items__course=course
        ).exists()
        
        paid_status = "✅ PAID" if (has_paid or has_paid_new) else "❌ UNPAID"
        print(f"  • {user.email} - {paid_status}")
    
    print()
    print("🚨 SECURITY CHECK:")
    unauthorized = enrollments.exclude(
        user__in=Order.objects.filter(
            course=course,
            status=Order.STATUS_PAID
        ).values_list('user', flat=True)
    ).exclude(
        user__in=Order.objects.filter(
            status=Order.STATUS_PAID,
            items__course=course
        ).values_list('user', flat=True)
    )
    
    if unauthorized:
        print(f"⚠️  Found {unauthorized.count()} unauthorized enrollments!")
        for enrollment in unauthorized:
            print(f"   - {enrollment.user.email} (enrolled without payment)")
            # Delete unauthorized enrollment
            enrollment.delete()
            print(f"   ✅ Removed unauthorized enrollment for {enrollment.user.email}")
    else:
        print("✅ All enrollments are properly authorized")

if __name__ == '__main__':
    check_enrollments()