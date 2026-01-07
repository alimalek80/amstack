from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import markdown
import bleach
from pygments.formatters import HtmlFormatter


class Category(models.Model):
    """Category model with parent/child relationships for sidebar navigation."""
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'slug': self.slug})
    
    @property
    def is_parent(self):
        return self.parent is None
    
    @classmethod
    def get_parent_categories(cls):
        """Get all parent categories with their subcategories."""
        return cls.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')


class Tag(models.Model):
    """Tag model for categorizing blog posts."""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(max_length=20, default='indigo')  # Tailwind color
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'slug': self.slug})


class Course(models.Model):
    """Course model for grouping related tutorials into a series."""
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='courses/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:course_detail', kwargs={'slug': self.slug})
    
    @property
    def total_lessons(self):
        return self.posts.count()
    
    @property
    def published_lessons(self):
        return self.posts.filter(is_published=True).count()


class Post(models.Model):
    """Blog post model with Markdown support."""
    
    POST_TYPE_CHOICES = [
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
        ('lesson', 'Course Lesson'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary for cards and SEO')
    content = models.TextField(help_text='Write in Markdown format')
    
    # Media
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Publishing
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Access control
    is_free = models.BooleanField(default=True)
    
    # Type and organization
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='tutorial')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    order = models.PositiveIntegerField(default=0, help_text='Order within a course')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='posts',
        help_text='Category for sidebar navigation'
    )
    
    # Relations
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='blog_posts'
    )
    
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
        """Estimate reading time in minutes."""
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
    
    @property
    def content_html(self):
        """Convert Markdown content to safe HTML with syntax highlighting."""
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'toc',
            'nl2br',
            'sane_lists',
        ], extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
            }
        })
        
        html = md.convert(self.content)
        
        # Sanitize HTML while allowing code blocks and common tags
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 's', 'blockquote',
            'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'pre', 'code', 'div', 'span', 'a', 'img', 'table',
            'thead', 'tbody', 'tr', 'th', 'td', 'hr',
        ]
        allowed_attrs = {
            '*': ['class', 'id'],
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
        }
        
        clean_html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        
        return clean_html
    
    @property
    def is_locked(self):
        """Check if post requires purchase to view."""
        return not self.is_free


class SavedPost(models.Model):
    """Model to track user's saved/bookmarked posts."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_posts'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.email} saved {self.post.title}"


class CourseEnrollment(models.Model):
    """Track user enrollment in courses (for paid courses)."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)  # Percentage
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"

