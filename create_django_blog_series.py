#!/usr/bin/env python
"""
Create a complete Django Blog App tutorial series
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from blog.models import Post, Category, Tag, Course
from django.utils import timezone

# Get or create category
django_category, _ = Category.objects.get_or_create(
    slug='django-tutorials',
    defaults={'name': 'Django Tutorials', 'order': 1}
)

# Get or create blog subcategory
blog_category, _ = Category.objects.get_or_create(
    slug='django-blog',
    defaults={'name': 'Django Blog', 'parent': django_category, 'order': 1}
)

# Create or get tags
from django.utils.text import slugify

tags_data = ['django', 'python', 'tutorial', 'beginner', 'intermediate', 'database', 'models', 'views', 'templates', 'forms']
tags = []
for tag_name in tags_data:
    tag, _ = Tag.objects.get_or_create(
        slug=slugify(tag_name),
        defaults={'name': tag_name}
    )
    tags.append(tag)

# Create the course
course, _ = Course.objects.get_or_create(
    slug='complete-django-blog-series',
    defaults={
        'title': 'Complete Django Blog App - From Zero to Hero',
        'description': 'A comprehensive series teaching you how to build a fully-featured blog application using Django. Learn models, views, templates, forms, and more!',
        'is_published': True,
        'is_free': True,
    }
)

# Tutorial 1: Getting Started
post1_content = """# Getting Started with Django Blog Development

Welcome to the complete Django Blog App tutorial series! In this first lesson, we'll set up our project and understand the fundamentals.

## What You'll Learn

In this comprehensive series, we'll build a complete blog application with:

- **Models**: Custom User, Post, Category, Tag, and Course models
- **Views**: Class-based and function-based views for listing, creating, and displaying posts
- **Templates**: Beautiful, responsive templates using Tailwind CSS
- **Forms**: Custom forms with validation
- **Authentication**: User registration, login, and permissions
- **Search & Filtering**: Category and tag-based filtering
- **Admin Interface**: Fully customized Django admin
- **Advanced Features**: Markdown support, code syntax highlighting, saved posts, and more

## Prerequisites

Before starting, make sure you have:

- Python 3.8 or higher
- pip (Python package manager)
- A code editor (VS Code, PyCharm, etc.)
- Basic Python knowledge
- Familiarity with command line/terminal

## Project Setup

### Step 1: Create a Virtual Environment

```bash
# Create a project directory
mkdir django-blog-project
cd django-blog-project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\\Scripts\\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Django

```bash
pip install django==6.0.1
```

### Step 3: Create Django Project

```bash
django-admin startproject amstack .
```

This creates the main project configuration.

### Step 4: Create Django App

```bash
python manage.py startapp blog
```

This creates the blog application where we'll build our features.

## Project Structure

After setup, your project should look like:

```
django-blog-project/
├── .venv/
├── amstack/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── blog/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
└── requirements.txt
```

## Installing Additional Packages

We'll need some additional packages for our blog:

```bash
pip install python-markdown bleach pillow django-crispy-forms crispy-tailwind
```

**Package explanations:**
- `python-markdown`: Renders markdown content to HTML
- `bleach`: Sanitizes HTML for security
- `pillow`: Image handling for cover images
- `django-crispy-forms`: Form rendering utilities
- `crispy-tailwind`: Tailwind CSS integration for forms

## Adding the App to Settings

Edit `amstack/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # Add this
    'crispy_forms',  # Add this
    'crispy_tailwind',  # Add this
]

# Add these at the end of settings.py
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
```

## Summary

You've successfully set up your Django project! In the next lesson, we'll create the Post and Category models that form the foundation of our blog.

**Next Steps:**
- Familiarize yourself with the project structure
- Test that everything works by running `python manage.py runserver`
- You should see the Django welcome page at http://localhost:8000

Ready for the next lesson? Let's build the models!"""

post1, _ = Post.objects.get_or_create(
    slug='01-getting-started-django-blog',
    defaults={
        'title': '01 - Getting Started with Django Blog Development',
        'excerpt': 'Set up your Django project, understand the project structure, and install required packages for building a complete blog application.',
        'content': post1_content,
        'is_published': True,
        'is_free': True,
        'is_featured': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 1,
    }
)
post1.tags.set(tags[:3])  # django, python, tutorial

# Tutorial 2: Creating Models
post2_content = """# Building the Blog Models

Now that we have our Django project set up, let's create the database models that will power our blog application.

## Understanding Django Models

A Django model is a Python class that represents a database table. Each attribute represents a database field. Django ORM (Object-Relational Mapping) handles all the database operations for us.

## Creating the Post Model

The Post model is the heart of our blog. Let's create it in `blog/models.py`:

```python
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

class Post(models.Model):
    # Basic fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    
    # Media
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Publishing
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def reading_time(self):
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
```

**Key Features Explained:**

- `title`: The blog post title
- `slug`: URL-friendly version of the title (automatically generated)
- `excerpt`: Short summary for cards and SEO
- `content`: Full post content (we'll use Markdown)
- `cover_image`: Featured image for the post
- `is_published`: Control visibility
- `published_at`: Automatic timestamp when published
- `reading_time`: Calculate estimated reading time

## Creating the Category Model

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

## Creating the Tag Model

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

## Connecting Models

Update the Post model to include relationships:

```python
class Post(models.Model):
    # ... existing fields ...
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
```

## Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the database tables based on our models.

## Next Steps

Now that our models are ready, we'll create Django admin configuration to manage our posts easily!"""

post2, _ = Post.objects.get_or_create(
    slug='02-building-blog-models',
    defaults={
        'title': '02 - Building the Blog Models',
        'excerpt': 'Create database models for posts, categories, and tags. Learn about Django ORM, relationships, and model features.',
        'content': post2_content,
        'is_published': True,
        'is_free': True,
        'is_featured': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 2,
    }
)
post2.tags.set([tags[0], tags[4], tags[5]])  # django, intermediate, database

# Tutorial 3: Django Admin Setup
post3_content = """# Setting Up Django Admin for Your Blog

Django's admin interface is one of its killer features. Let's configure it to manage our blog posts like a pro.

## Registering Models in Admin

Edit `blog/admin.py`:

```python
from django.contrib import admin
from .models import Post, Category, Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'category', 'reading_time', 'published_at')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Organization', {
            'fields': ('category', 'tags')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
```

## Creating a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

## Accessing Admin

```bash
python manage.py runserver
```

Visit http://localhost:8000/admin and log in with your credentials.

## Admin Features Explained

- `list_display`: Columns shown in the list view
- `list_filter`: Sidebar filters
- `search_fields`: Searchable fields
- `prepopulated_fields`: Auto-fill slug from title
- `fieldsets`: Organize fields into sections
- `readonly_fields`: Fields that can't be edited

## Creating Sample Data

Create a few posts through the admin interface to test everything is working!

**Next Lesson:** We'll create views to display these posts on the frontend."""

post3, _ = Post.objects.get_or_create(
    slug='03-django-admin-setup',
    defaults={
        'title': '03 - Setting Up Django Admin for Your Blog',
        'excerpt': 'Configure Django admin interface to easily manage posts, categories, and tags. Learn fieldsets, filters, and customization.',
        'content': post3_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 3,
    }
)
post3.tags.set([tags[0], tags[2], tags[3]])  # django, tutorial, beginner

# Tutorial 4: Views and URLs
post4_content = """# Creating Views and URL Routing

Now let's create the views that will display our blog posts to users.

## Creating Views

Edit `blog/views.py`:

```python
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    
    # Filter by category if provided
    category_slug = request.GET.get('category', '')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    context = {
        'posts': posts,
        'categories': Category.objects.all(),
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    related_posts = Post.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)

def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, is_published=True)
    
    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog/tag_posts.html', context)
```

## Setting Up URLs

Create `blog/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
```

Include in main `amstack/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
]
```

## Understanding URL Parameters

- `<slug:slug>` - URL parameter that matches the slug field
- `name='post_list'` - URL name for reverse lookups in templates
- `app_name = 'blog'` - Namespace to avoid URL name conflicts

## Testing Views

```bash
python manage.py runserver
```

Visit:
- http://localhost:8000/blog/ - List of posts
- http://localhost:8000/blog/your-post-slug/ - Individual post

**Next Lesson:** Creating beautiful templates!"""

post4, _ = Post.objects.get_or_create(
    slug='04-views-and-urls',
    defaults={
        'title': '04 - Creating Views and URL Routing',
        'excerpt': 'Build views to display posts and set up URL routing. Learn function-based views, URL parameters, and template context.',
        'content': post4_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 4,
    }
)
post4.tags.set([tags[0], tags[2], tags[8]])  # django, tutorial, views

# Tutorial 5: Templates and Styling
post5_content = """# Building Templates with Tailwind CSS

Let's create beautiful, responsive templates for displaying our blog.

## Directory Structure

Create this structure in your project:

```
templates/
├── base.html
├── blog/
│   ├── post_list.html
│   ├── post_detail.html
│   └── tag_posts.html
```

## Base Template

Create `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Django Blog{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold text-indigo-600">My Blog</h1>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-gray-900 text-white mt-12 py-8">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p>&copy; 2024 My Django Blog. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
```

## Post List Template

Create `templates/blog/post_list.html`:

```html
{% extends 'base.html' %}

{% block title %}Blog Posts{% endblock %}

{% block content %}
<div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-4">Latest Posts</h1>
</div>

<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for post in posts %}
    <article class="bg-white rounded-lg shadow hover:shadow-lg transition">
        {% if post.cover_image %}
        <img src="{{ post.cover_image.url }}" alt="{{ post.title }}" 
             class="w-full h-48 object-cover rounded-t-lg">
        {% endif %}
        
        <div class="p-6">
            <h2 class="text-xl font-bold mb-2">
                <a href="{{ post.get_absolute_url }}" 
                   class="hover:text-indigo-600">{{ post.title }}</a>
            </h2>
            
            <p class="text-gray-600 mb-4">{{ post.excerpt }}</p>
            
            <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500">
                    {{ post.reading_time }} min read
                </span>
                <a href="{{ post.get_absolute_url }}" 
                   class="text-indigo-600 font-semibold hover:text-indigo-700">
                    Read More →
                </a>
            </div>
        </div>
    </article>
    {% endfor %}
</div>
{% endblock %}
```

## Post Detail Template

Create `templates/blog/post_detail.html`:

```html
{% extends 'base.html' %}

{% block title %}{{ post.title }}{% endblock %}

{% block content %}
<article class="max-w-3xl">
    <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ post.title }}</h1>
    
    <div class="flex gap-4 text-gray-600 mb-6">
        <span>{{ post.published_at|date:"M d, Y" }}</span>
        <span>{{ post.reading_time }} min read</span>
        {% if post.category %}
        <span>{{ post.category.name }}</span>
        {% endif %}
    </div>
    
    {% if post.cover_image %}
    <img src="{{ post.cover_image.url }}" alt="{{ post.title }}" 
         class="w-full h-96 object-cover rounded-lg mb-8">
    {% endif %}
    
    <div class="prose prose-lg">
        {{ post.content|safe }}
    </div>
    
    <!-- Tags -->
    {% if post.tags.all %}
    <div class="mt-8">
        <strong>Tags:</strong>
        {% for tag in post.tags.all %}
        <a href="{% url 'blog:tag_posts' tag.slug %}" 
           class="inline-block mr-2 px-3 py-1 bg-indigo-100 
                  text-indigo-700 rounded hover:bg-indigo-200">
            #{{ tag.name }}
        </a>
        {% endfor %}
    </div>
    {% endif %}
    
    <!-- Related Posts -->
    {% if related_posts %}
    <div class="mt-12 pt-8 border-t">
        <h3 class="text-2xl font-bold mb-6">Related Posts</h3>
        <div class="grid md:grid-cols-3 gap-6">
            {% for related in related_posts %}
            <a href="{{ related.get_absolute_url }}" 
               class="hover:text-indigo-600">
                <h4 class="font-semibold">{{ related.title }}</h4>
                <p class="text-sm text-gray-600">{{ related.excerpt }}</p>
            </a>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</article>
{% endblock %}
```

## Configuring Templates

Update `amstack/settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Visit http://localhost:8000/blog/ to see your beautiful blog!

**Next Lesson:** Adding user authentication and comments."""

post5, _ = Post.objects.get_or_create(
    slug='05-templates-tailwind-css',
    defaults={
        'title': '05 - Building Templates with Tailwind CSS',
        'excerpt': 'Create responsive, beautiful templates using Tailwind CSS. Learn template inheritance, tags, and styling.',
        'content': post5_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 5,
    }
)
post5.tags.set([tags[0], tags[2], tags[9]])  # django, tutorial, templates

print("✅ Django Blog Tutorial Series Created Successfully!")
print(f"\n📚 Course: {course.title}")
print(f"📖 Posts created: {Post.objects.filter(course=course).count()}")
print("\nTutorial Posts:")
for post in Post.objects.filter(course=course).order_by('order'):
    print(f"  - {post.title}")
print("\n🚀 Visit http://localhost:8000/blog/ to see the tutorials!")
