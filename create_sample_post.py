#!/usr/bin/env python
"""
Create a sample blog post about custom user model and profile creation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from blog.models import Post, Category, Tag
from django.utils import timezone

# Get or create category
category, _ = Category.objects.get_or_create(
    slug='django-backend',
    defaults={'name': 'Django Backend'}
)

# Get existing tags that we can use
existing_tags = Tag.objects.filter(name__in=['django', 'tutorial', 'authentication'])
tags = list(existing_tags) if existing_tags.exists() else []

# Post content in markdown
post_content = """# Creating a Custom User Model with Auto-Profile in Django

Building scalable Django applications requires careful planning of your user authentication system. In this complete guide, we'll create a custom user model and automatically generate user profiles.

## Why Custom User Model?

Django's default User model is excellent for most projects, but custom user models give you:

- **Flexibility**: Use email instead of username for authentication
- **Extensibility**: Add custom fields without creating separate models
- **Best practices**: Recommended by Django documentation for production apps
- **Control**: Manage your authentication exactly as needed

## Prerequisites

Before starting, ensure you have:

```python
Django 4.0+
Python 3.8+
Basic Django knowledge
```

## Step 1: Create the Accounts App

First, create a new app for handling user authentication:

```bash
python manage.py startapp accounts
```

Then add it to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # Add this
]
```

## Step 2: Create Custom User Model

Create a custom user model that uses email as the unique identifier:

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    '''Custom user model using email instead of username'''
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
```

## Step 3: Configure Custom User in Settings

Update your `settings.py` to use the custom user model:

```python
# settings.py
AUTH_USER_MODEL = 'accounts.CustomUser'
```

**Important**: Do this BEFORE creating migrations!

## Step 4: Create User Profile Model

Create a profile model to store additional user information:

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    '''Custom user model using email instead of username'''
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    '''Extended user profile'''
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    company = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.email} Profile'
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
```

## Step 5: Auto-Create Profile with Signals

Use Django signals to automatically create a profile when a user is created:

```python
# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    '''Create a UserProfile when a CustomUser is created'''
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    '''Save the UserProfile when the CustomUser is saved'''
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

Register signals in your app config:

```python
# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals
```

## Step 6: Register with Django Admin

Create a custom admin interface for your user model:

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    fields = ('bio', 'avatar', 'company', 'location', 'website')
    extra = 0

class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'location', 'created_at')
    search_fields = ('user__email', 'company', 'location')
    readonly_fields = ('created_at', 'updated_at')
```

## Step 7: Create and Run Migrations

Create migrations for your new models:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

## Step 8: Create Superuser

Create an admin user:

```bash
python manage.py createsuperuser
```

Enter your email and password when prompted.

## Step 9: Verify in Admin

1. Go to `http://localhost:8000/admin`
2. Login with your credentials
3. Create a new custom user
4. Notice that the UserProfile is automatically created!

## Advanced: Custom User Manager

For complete customization, create a custom manager:

```python
# accounts/managers.py
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
```

Then use it in your CustomUser model:

```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    objects = CustomUserManager()
    # ... rest of fields
```

## Common Issues & Solutions

### Issue: User table doesn't exist
**Solution**: Run migrations with `python manage.py migrate`

### Issue: Signal not firing
**Solution**: Ensure signals are registered in `apps.py` ready method

### Issue: Profile not creating for existing users
**Solution**: Create profiles for existing users:
```python
from accounts.models import CustomUser, UserProfile
for user in CustomUser.objects.all():
    UserProfile.objects.get_or_create(user=user)
```

## Best Practices

1. **Always use custom user models from project start** - Difficult to change mid-project
2. **Use signals for related model creation** - Keeps code DRY and organized
3. **Separate profile from user model** - Follows single responsibility principle
4. **Use email for auth** - More user-friendly than username
5. **Validate emails** - Consider using verification tokens

## Testing

Create simple tests for your custom user:

```python
# accounts/tests.py
from django.test import TestCase
from .models import CustomUser, UserProfile

class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_created(self):
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_profile_auto_created(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
```

## Conclusion

You now have a production-ready custom user model with automatic profile creation! This setup provides:

- Email-based authentication
- Extended user information via profiles
- Automatic profile creation with signals
- Clean admin interface
- Scalable architecture

This is the foundation for user management in real Django applications. Build on this with additional features like email verification, two-factor authentication, and social login as needed.

Happy coding! 🚀
"""

# Create the post
post = Post.objects.create(
    title='Creating a Custom User Model with Auto-Profile in Django',
    slug='custom-user-model-django-profile',
    excerpt='Complete guide to building a custom Django user model with email authentication and auto-generated user profiles using signals.',
    content=post_content,
    author=None,
    category=category,
    is_free=True,
    is_published=True,
    is_featured=False,
    created_at=timezone.now(),
)

# Add tags
post.tags.add(*tags)

print(f"✅ Post created successfully!")
print(f"Title: {post.title}")
print(f"Slug: {post.slug}")
print(f"Category: {post.category.name}")
print(f"Tags: {', '.join([tag.name for tag in post.tags.all()])}")
