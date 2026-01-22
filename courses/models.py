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
    
    # SEO fields (all optional to preserve existing courses)
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
        help_text='Meta description for search engines (160 chars max, if empty will use description)'
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
    og_image_alt = models.CharField(
        max_length=125, 
        blank=True, 
        null=True,
        help_text='Alt text for Open Graph image'
    )
    schema_type = models.CharField(
        max_length=50,
        choices=[
            ('Course', 'Course'),
            ('LearningResource', 'Learning Resource'),
            ('EducationalOrganization', 'Educational Content'),
        ],
        default='Course',
        help_text='Schema.org type for structured data'
    )
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
    
    @property
    def get_seo_title(self):
        """Return SEO title or fallback to main title."""
        return self.seo_title or self.title
    
    @property
    def get_meta_description(self):
        """Return meta description or fallback to description."""
        if self.meta_description:
            return self.meta_description
        # Truncate description to 160 chars if too long
        if len(self.description) > 160:
            return self.description[:157] + "..."
        return self.description
    
    @property
    def get_keywords_list(self):
        """Return keywords as a list."""
        if self.meta_keywords:
            return [kw.strip() for kw in self.meta_keywords.split(',') if kw.strip()]
        return []
    
    def get_structured_data(self):
        """Generate JSON-LD structured data for the course."""
        import json
        
        data = {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            "name": self.get_seo_title,
            "description": self.get_meta_description,
            "provider": {
                "@type": "Organization",
                "name": "Amstack"
            },
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online"
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
            
        # Add pricing info
        if not self.is_free:
            data["offers"] = {
                "@type": "Offer",
                "price": str(self.price),
                "priceCurrency": "USD"
            }
        
        return json.dumps(data, indent=2)


class Lesson(models.Model):
    """Course lesson content with Markdown support."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, help_text='Short summary for cards and SEO')
    content = models.TextField(help_text='Write in Markdown format')
    cover_image = models.ImageField(upload_to='lessons/', blank=True, null=True)
    
    # SEO fields (all optional to preserve existing lessons)
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
    og_image_alt = models.CharField(
        max_length=125, 
        blank=True, 
        null=True,
        help_text='Alt text for Open Graph image'
    )
    reading_time_override = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text='Manual reading time in minutes (if empty, will be calculated)'
    )
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
        if self.reading_time_override:
            return self.reading_time_override
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))
    
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
    
    def get_structured_data(self):
        """Generate JSON-LD structured data for the lesson."""
        import json
        
        data = {
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": self.get_seo_title,
            "description": self.get_meta_description,
            "isPartOf": {
                "@type": "Course",
                "name": self.course.title
            },
            "provider": {
                "@type": "Organization",
                "name": "Amstack"
            },
            "datePublished": self.published_at.isoformat() if self.published_at else self.created_at.isoformat(),
            "dateModified": self.updated_at.isoformat(),
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
    last_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollment_last_seen'
    )

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.email} enrolled in {self.course.title}"

    def get_continue_lesson(self):
        """Return the lesson the user should resume from."""
        lessons = list(self.course.lessons.filter(is_published=True).order_by('order', 'created_at'))
        if not lessons:
            return None

        # If we have a last seen lesson, try to return it; otherwise start at the first lesson
        if self.last_lesson and self.last_lesson in lessons:
            return self.last_lesson

        return lessons[0]
