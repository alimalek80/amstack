from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
import markdown
import bleach


class Course(models.Model):
    """Course model to group lessons into a series."""

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
        return reverse('courses:course_detail', kwargs={'slug': self.slug})

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def published_lessons(self):
        return self.lessons.filter(is_published=True).count()


class Lesson(models.Model):
    """Course lesson content with Markdown support."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary for cards and SEO')
    content = models.TextField(help_text='Write in Markdown format')
    cover_image = models.ImageField(upload_to='lessons/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    is_free = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Order within a course')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:lesson_detail', kwargs={'course_slug': self.course.slug, 'slug': self.slug})

    @property
    def reading_time(self):
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))

    @property
    def content_html(self):
        """Convert Markdown content to sanitized HTML."""
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

        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    @property
    def is_paid(self):
        return not self.is_free


class CourseEnrollment(models.Model):
    """Track user enrollment in courses."""

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
    progress = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"
