#!/usr/bin/env python
"""
Create a sample paid blog post for local testing.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from django.utils import timezone
from blog.models import Post, Category, Tag


def main():
    category, _ = Category.objects.get_or_create(
        slug='premium-django',
        defaults={'name': 'Premium Django'}
    )

    # Get or create tags
    tag_names = ['Django', 'premium', 'architecture']  # Use 'Django' with capital D
    tags = []
    for name in tag_names:
        try:
            tag = Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=name)
        tags.append(tag)

    post, created = Post.objects.get_or_create(
        slug='django-saas-architecture',
        defaults={
            'title': 'Designing a Production-Ready Django SaaS',
            'excerpt': 'A hands-on guide to multi-tenant architecture, background jobs, and observability in Django.',
            'content': PAID_CONTENT.strip(),
            'category': category,
            'is_published': True,
            'published_at': timezone.now(),
            'is_featured': True,
            'is_free': False,
            'price': 49.00,
            'post_type': 'tutorial',
        }
    )

    if created:
        post.tags.set(tags)
        print('Created paid post: django-saas-architecture')
    else:
        print('Paid post already exists: django-saas-architecture')


PAID_CONTENT = """
# Designing a Production-Ready Django SaaS

In this premium guide we build a resilient SaaS stack on Django:

- Multi-tenant separation with custom middleware and router
- Stripe-backed billing and webhooks
- Task offloading with Celery and Redis
- Observability with structured logging and OpenTelemetry traces
- Zero-downtime deploys and blue-green migrations

## Architecture Diagram

We use a split architecture: Django API, worker pool, PostgreSQL, Redis, and S3-backed storage. Traffic enters through Nginx/Traefik with TLS termination, then heads to the app tier. A sidecar handles metrics and traces.

## Key Models

- `Account` for tenant isolation
- `Subscription` tracking Stripe product and status
- `AuditLog` for security and compliance

## Deployment Checklist

- Health checks per service
- Database connection pooling
- Idempotent migrations
- Rollback strategy per release

Download the repo bundle inside the course to follow along step by step.
"""

if __name__ == '__main__':
    main()
