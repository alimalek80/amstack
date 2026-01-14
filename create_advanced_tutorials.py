#!/usr/bin/env python
"""
Add advanced tutorials to the Django Blog series
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from blog.models import Post, Category, Tag, Course
from django.utils import timezone
from django.utils.text import slugify

# Get existing course and category
course = Course.objects.get(slug='complete-django-blog-series')
blog_category = Category.objects.get(slug='django-blog')

# Get tags
django_tag = Tag.objects.get(slug='django')
tutorial_tag = Tag.objects.get(slug='tutorial')
intermediate_tag = Tag.objects.get(slug='intermediate')
forms_tag = Tag.objects.get(slug='forms')

# Tutorial 6: Working with Forms
post6_content = """# Creating and Handling Forms

Forms are crucial for user interactions. Let's learn how to create forms for blog comments and post creation.

## Django Forms Basics

Create `blog/forms.py`:

```python
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'content', 'cover_image', 'category', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Enter post title'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Short summary of your post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg font-mono',
                'rows': 15,
                'placeholder': 'Write in Markdown format'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
            'tags': forms.CheckboxSelectMultiple(),
        }

class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Your email'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'rows': 5,
            'placeholder': 'Your comment'
        })
    )
```

## Using Forms in Views

Update `blog/views.py`:

```python
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save many-to-many fields
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form})

def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Save comment (you'd need a Comment model)
            return redirect('blog:post_detail', slug=slug)
    else:
        form = CommentForm()
    
    return render(request, 'blog/add_comment.html', {
        'form': form,
        'post': post
    })
```

## Form Templates

Create `templates/blog/post_form.html`:

```html
{% extends 'base.html' %}

{% block title %}Create Post{% endblock %}

{% block content %}
<div class="max-w-3xl">
    <h1 class="text-3xl font-bold mb-8">Create New Post</h1>
    
    <form method="post" enctype="multipart/form-data" class="space-y-6">
        {% csrf_token %}
        
        {% if form.non_field_errors %}
        <div class="p-4 bg-red-100 text-red-700 rounded">
            {{ form.non_field_errors }}
        </div>
        {% endif %}
        
        {% for field in form %}
        <div>
            {{ field.label_tag }}
            {{ field }}
            {% if field.errors %}
            <span class="text-red-600 text-sm">{{ field.errors }}</span>
            {% endif %}
        </div>
        {% endfor %}
        
        <button type="submit" class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Create Post
        </button>
    </form>
</div>
{% endblock %}
```

## Key Concepts

- **ModelForm**: Automatically create forms from models
- **widgets**: Customize form field rendering
- **CSRF Token**: Security feature (always use {% csrf_token %})
- **request.FILES**: Handle file uploads
- **save_m2m()**: Save many-to-many relationships

**Next Lesson:** User authentication and permissions."""

post6, created = Post.objects.get_or_create(
    slug='06-working-with-forms',
    defaults={
        'title': '06 - Creating and Handling Forms',
        'excerpt': 'Learn how to create and handle forms in Django. Build forms for blog posts and comments with validation.',
        'content': post6_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 6,
    }
)
if created:
    post6.tags.set([django_tag, forms_tag, intermediate_tag])

# Tutorial 7: Advanced Features
post7_content = """# Advanced Features: Markdown, Search, and Pagination

Let's add professional features to make our blog stand out.

## Markdown Support

Add markdown rendering to your Post model:

```python
import markdown
from django.utils.safestring import mark_safe

@property
def content_html(self):
    '''Convert Markdown to HTML'''
    md = markdown.Markdown(
        extensions=['fenced_code', 'codehilite', 'tables', 'toc']
    )
    return mark_safe(md.convert(self.content))
```

Update your template:

```html
<div class="prose max-w-none">
    {{ post.content_html }}
</div>
```

## Search Functionality

Add to `blog/views.py`:

```python
from django.db.models import Q

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    
    # Search feature
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    context = {
        'posts': posts,
        'search_query': search_query,
    }
    return render(request, 'blog/post_list.html', context)
```

## Pagination

Add to your view:

```python
from django.core.paginator import Paginator

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    
    # Pagination
    paginator = Paginator(posts, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/post_list.html', context)
```

Template pagination:

```html
{% if page_obj.has_other_pages %}
<div class="flex justify-center gap-2 mt-8">
    {% if page_obj.has_previous %}
        <a href="?page=1" class="px-4 py-2 bg-gray-200 rounded">First</a>
        <a href="?page={{ page_obj.previous_page_number }}" class="px-4 py-2 bg-gray-200 rounded">Previous</a>
    {% endif %}
    
    <span class="px-4 py-2">
        Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
    </span>
    
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}" class="px-4 py-2 bg-gray-200 rounded">Next</a>
        <a href="?page={{ page_obj.paginator.num_pages }}" class="px-4 py-2 bg-gray-200 rounded">Last</a>
    {% endif %}
</div>
{% endif %}
```

## Reading Time Calculation

```python
@property
def reading_time(self):
    '''Estimate reading time in minutes'''
    word_count = len(self.content.split())
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"
```

These features will make your blog feel professional and user-friendly!

**Next Lesson:** Deployment and going live."""

post7, created = Post.objects.get_or_create(
    slug='07-advanced-features-markdown-search',
    defaults={
        'title': '07 - Advanced Features: Markdown, Search, and Pagination',
        'excerpt': 'Add professional features like Markdown rendering, search functionality, and pagination to your blog.',
        'content': post7_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 7,
    }
)
if created:
    post7.tags.set([django_tag, tutorial_tag, intermediate_tag])

# Tutorial 8: Deployment
post8_content = """# Deploying Your Django Blog to Production

Ready to share your blog with the world? Let's deploy it!

## Pre-Deployment Checklist

### 1. Security Settings

Update `amstack/settings.py`:

```python
# Set to False in production
DEBUG = False

# Add your domain
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

### 2. Static and Media Files

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. Environment Variables

Create `.env` file:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

Install python-decouple:

```bash
pip install python-decouple
```

Update settings.py:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
```

## Deployment Options

### Option 1: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

### Option 2: DigitalOcean App Platform

1. Push code to GitHub
2. Connect GitHub repository to DigitalOcean
3. Set environment variables
4. Deploy!

### Option 3: PythonAnywhere

1. Upload code via git
2. Configure virtual environment
3. Set up web app
4. Enable SSL certificate

## Post-Deployment

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Set Up Email

```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

Congratulations! Your blog is now live! 🎉

**Keep Learning:**
- Add user comments
- Implement email subscriptions
- Add social sharing
- Set up analytics
- Optimize for SEO"""

post8, created = Post.objects.get_or_create(
    slug='08-deploying-to-production',
    defaults={
        'title': '08 - Deploying Your Django Blog to Production',
        'excerpt': 'Learn how to prepare and deploy your Django blog to production. Cover security, deployment platforms, and best practices.',
        'content': post8_content,
        'is_published': True,
        'is_free': True,
        'published_at': timezone.now(),
        'post_type': 'lesson',
        'course': course,
        'category': blog_category,
        'order': 8,
    }
)
if created:
    post8.tags.set([django_tag, tutorial_tag, intermediate_tag])

print("\n✅ Advanced Tutorials Added Successfully!")
print(f"\n📖 Total posts in series: {Post.objects.filter(course=course).count()}")
print("\n📚 Complete Tutorial Series:")
for post in Post.objects.filter(course=course).order_by('order'):
    print(f"  ✓ {post.title}")
