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
            return f"{self.parent.name} > {self.name}"  # Temporarily using > instead of →
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
    
    def has_posts(self):
        """Check if category or its subcategories have any published posts."""
        from django.db.models import Q
        category_ids = [self.id]
        if self.is_parent:
            category_ids.extend(self.subcategories.values_list('id', flat=True))
        return Post.objects.filter(
            category_id__in=category_ids,
            is_published=True
        ).exists()
    
    @classmethod
    def get_parent_categories(cls):
        """Get all parent categories with their subcategories that have posts."""
        parents = cls.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
        
        # Filter to only parents that have posts or have subcategories with posts
        result = []
        for parent in parents:
            if parent.has_posts():
                result.append(parent)
        
        return result


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


class Post(models.Model):
    """Blog post model with Markdown support."""
    
    POST_TYPE_CHOICES = [
        ('tutorial', 'Tutorial'),
        ('article', 'Article'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary for cards and SEO')
    content = models.TextField(help_text='Write in Markdown format')
    
    # SEO fields (all optional to preserve existing posts)
    seo_title = models.CharField(
        max_length=60, 
        blank=True, 
        null=True,
        help_text='SEO optimized title (60 chars max, if empty will use main title)'
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        null=True,
        help_text='Meta description for search engines (160 chars max, if empty will use excerpt)'
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text='Comma-separated keywords for SEO'
    )
    focus_keyword = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Primary keyword to focus on for SEO'
    )
    canonical_url = models.URLField(
        blank=True, 
        null=True,
        help_text='Canonical URL if this is republished content'
    )
    og_image_alt = models.CharField(
        max_length=125, 
        blank=True, 
        null=True,
        help_text='Alt text for Open Graph image'
    )
    schema_type = models.CharField(
        max_length=50,
        choices=[
            ('Article', 'Article'),
            ('BlogPosting', 'Blog Post'),
            ('TechArticle', 'Technical Article'),
            ('Tutorial', 'Tutorial'),
            ('HowTo', 'How-To Guide'),
        ],
        default='BlogPosting',
        help_text='Schema.org type for structured data'
    )
    reading_time_override = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text='Manual reading time in minutes (if empty, will be calculated)'
    )
    
    # Media
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    # Publishing
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Access control
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Analytics
    views = models.PositiveIntegerField(default=0)
    
    # Type and organization
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='tutorial')
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
        if self.reading_time_override:
            return self.reading_time_override
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
    
    @property
    def get_seo_title(self):
        """Return SEO title or fallback to main title."""
        return self.seo_title or self.title
    
    @property
    def get_meta_description(self):
        """Return meta description or fallback to excerpt."""
        return self.meta_description or self.excerpt
    
    @property
    def get_keywords_list(self):
        """Return keywords as a list."""
        if self.meta_keywords:
            return [kw.strip() for kw in self.meta_keywords.split(',') if kw.strip()]
        return []
    
    @property
    def get_canonical_url(self):
        """Return canonical URL or the post's absolute URL."""
        return self.canonical_url or self.get_absolute_url()
    
    def get_structured_data(self):
        """Generate JSON-LD structured data for the post."""
        import json
        from django.urls import reverse
        from django.utils.html import strip_tags
        
        data = {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            "headline": self.get_seo_title,
            "description": self.get_meta_description,
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() if self.author else "Amstack"
            },
            "datePublished": self.published_at.isoformat() if self.published_at else self.created_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.get_absolute_url()
            }
        }
        
        if self.cover_image:
            data["image"] = {
                "@type": "ImageObject",
                "url": self.cover_image.url,
                "alt": self.og_image_alt or self.title
            }
        
        if self.focus_keyword:
            data["keywords"] = self.focus_keyword
        elif self.meta_keywords:
            data["keywords"] = self.meta_keywords
        
        return json.dumps(data, indent=2)
    
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

