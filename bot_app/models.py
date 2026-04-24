"""
Models for Telegram Media Downloader Bot
"""
from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    """Track Telegram users who interact with the bot."""
    
    telegram_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        verbose_name="Telegram User ID"
    )
    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Telegram Username"
    )
    first_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Last Name"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Is Blocked"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_interaction = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_telegram_users'
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'
        ordering = ['-last_interaction']

    def __str__(self):
        return f"{self.username or self.telegram_id} ({self.telegram_id})"


class DownloadRequest(models.Model):
    """Track all download requests."""
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('twitter', 'Twitter/X'),
        ('unknown', 'Unknown'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('uploading', 'Uploading'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    MEDIA_TYPE_CHOICES = [
        ('video', 'Video'),
        ('image', 'Image'),
        ('carousel', 'Carousel'),
    ]
    
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='downloads',
        verbose_name="User"
    )
    url = models.URLField(
        max_length=1000,
        verbose_name="Media URL"
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name="Platform"
    )
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Media Type"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="File Size (bytes)"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Error Message"
    )
    download_duration = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Download Duration (seconds)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bot_download_requests'
        verbose_name = 'Download Request'
        verbose_name_plural = 'Download Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['platform', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username or self.user.telegram_id} - {self.platform} - {self.status}"


class BotStatistics(models.Model):
    """Store daily statistics."""
    
    date = models.DateField(unique=True, db_index=True)
    total_requests = models.IntegerField(default=0)
    successful_downloads = models.IntegerField(default=0)
    failed_downloads = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    instagram_downloads = models.IntegerField(default=0)
    youtube_downloads = models.IntegerField(default=0)
    twitter_downloads = models.IntegerField(default=0)
    total_data_transferred = models.BigIntegerField(default=0)  # in bytes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_statistics'
        verbose_name = 'Bot Statistics'
        verbose_name_plural = 'Bot Statistics'
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date}"


class BotLog(models.Model):
    """Log important bot events."""
    
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info')
    message = models.TextField()
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    url = models.URLField(max_length=1000, null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'bot_logs'
        verbose_name = 'Bot Log'
        verbose_name_plural = 'Bot Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.level.upper()}] {self.message[:50]}"
