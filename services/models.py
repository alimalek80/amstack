from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import markdown
import bleach


class ServiceCategory(models.Model):
    """Categories for organizing services."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    """Represents a sellable developer service."""
    
    PRICING_CHOICES = [
        ('starting_at', 'Starting at'),
        ('fixed', 'Fixed price'),
        ('hourly', 'Hourly rate'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField()
    description = models.TextField()  # Supports Markdown/HTML
    
    pricing_type = models.CharField(
        max_length=20,
        choices=PRICING_CHOICES,
        default='starting_at'
    )
    starting_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    fixed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    timeline = models.CharField(max_length=100, blank=True)
    deliverables = models.TextField(blank=True)  # Newline-separated list
    requirements = models.TextField(blank=True)  # What client needs to provide
    faqs = models.TextField(blank=True)  # Q/A text or markdown
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['is_active', '-is_featured']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_deliverables_list(self):
        """Return deliverables as a list, split by newline."""
        if self.deliverables:
            return [item.strip() for item in self.deliverables.strip().split('\n') if item.strip()]
        return []

    def get_requirements_list(self):
        """Return requirements as a list, split by newline."""
        if self.requirements:
            return [item.strip() for item in self.requirements.strip().split('\n') if item.strip()]
        return []

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'slug': self.slug})

    @property
    def description_html(self):
        """Convert Markdown description to safe HTML."""
        if not self.description:
            return ""
        
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'nl2br',
            'sane_lists',
        ])
        
        html = md.convert(self.description)
        
        # Sanitize HTML while allowing common tags
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
            strip=True,
        )
        
        return clean_html
