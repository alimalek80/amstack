from __future__ import annotations

from typing import Optional
from .models import Order
from courses.models import CourseEnrollment, Course
from blog.models import Post
from services.models import Service


def user_has_post_access(user, post: Post) -> bool:
    if post.is_free:
        return True
    if not user.is_authenticated:
        return False
    
    # Check both legacy orders and new OrderItem structure
    legacy_access = Order.objects.filter(user=user, post=post, status=Order.STATUS_PAID).exists()
    if legacy_access:
        return True
    
    # Check new OrderItem structure
    new_access = Order.objects.filter(
        user=user,
        status=Order.STATUS_PAID,
        items__post=post
    ).exists()
    
    return new_access


def user_has_course_access(user, course: Course) -> bool:
    if course.is_free:
        return True
    if not user.is_authenticated:
        return False
    if CourseEnrollment.objects.filter(user=user, course=course).exists():
        return True
    
    # Check both legacy orders and new OrderItem structure
    legacy_access = Order.objects.filter(user=user, course=course, status=Order.STATUS_PAID).exists()
    if legacy_access:
        return True
    
    # Check new OrderItem structure
    new_access = Order.objects.filter(
        user=user,
        status=Order.STATUS_PAID,
        items__course=course
    ).exists()
    
    return new_access


def user_has_service_order(user, service: Service) -> bool:
    if not user.is_authenticated:
        return False
    
    # Check both legacy orders and new OrderItem structure
    legacy_access = Order.objects.filter(user=user, service=service, status=Order.STATUS_PAID).exists()
    if legacy_access:
        return True
    
    # Check new OrderItem structure
    new_access = Order.objects.filter(
        user=user,
        status=Order.STATUS_PAID,
        items__service=service
    ).exists()
    
    return new_access


def ensure_course_enrollment(user, course: Course) -> CourseEnrollment:
    """Create an enrollment for the user if it does not exist."""
    enrollment, _ = CourseEnrollment.objects.get_or_create(user=user, course=course)
    return enrollment


def get_paid_order(user, *, post: Optional[Post] = None, course: Optional[Course] = None, service: Optional[Service] = None) -> Optional[Order]:
    filters = {'user': user, 'status': Order.STATUS_PAID}
    if post:
        filters['post'] = post
    if course:
        filters['course'] = course
    if service:
        filters['service'] = service
    return Order.objects.filter(**filters).first()
