from django.db import models


class Lead(models.Model):
    """Model for storing lead inquiries from visitors."""
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=150, blank=True)
    
    service_slug = models.SlugField(max_length=200, blank=True)  # Store selected service slug
    service_title = models.CharField(max_length=200, blank=True)  # Store service title snapshot
    
    budget = models.CharField(max_length=80, blank=True)  # e.g., "$500-$1k"
    timeline = models.CharField(max_length=80, blank=True)  # e.g., "this week", "2-4 weeks"
    message = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    source = models.CharField(max_length=80, blank=True)  # e.g., "services", "blog", "direct"
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Leads"
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.email} - {self.get_status_display()}"

    @property
    def short_message(self):
        """Return first 120 characters of message."""
        return self.message[:120] + ("..." if len(self.message) > 120 else "")
