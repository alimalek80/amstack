"""
Admin interface for Telegram Bot
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser, DownloadRequest, BotStatistics, BotLog


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'is_blocked', 'last_interaction', 'created_at']
    list_filter = ['is_active', 'is_blocked', 'created_at', 'last_interaction']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at', 'last_interaction']
    actions = ['block_users', 'unblock_users']
    
    fieldsets = (
        ('User Information', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ('Status', {
            'fields': ('is_active', 'is_blocked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_interaction'),
            'classes': ('collapse',)
        }),
    )
    
    def block_users(self, request, queryset):
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} user(s) blocked successfully.')
    block_users.short_description = 'Block selected users'
    
    def unblock_users(self, request, queryset):
        updated = queryset.update(is_blocked=False)
        self.message_user(request, f'{updated} user(s) unblocked successfully.')
    unblock_users.short_description = 'Unblock selected users'


@admin.register(DownloadRequest)
class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'platform', 'media_type', 'status', 'file_size_mb', 'duration', 'created_at']
    list_filter = ['platform', 'status', 'media_type', 'created_at']
    search_fields = ['user__username', 'user__telegram_id', 'url']
    readonly_fields = ['user', 'url', 'platform', 'media_type', 'file_size', 'download_duration', 'created_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'url', 'platform', 'media_type')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Metrics', {
            'fields': ('file_size', 'download_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
        }),
    )
    
    def user_link(self, obj):
        return format_html('<a href="/admin/bot_app/telegramuser/{}/change/">{}</a>',
                          obj.user.id, obj.user.username or obj.user.telegram_id)
    user_link.short_description = 'User'
    
    def file_size_mb(self, obj):
        if obj.file_size:
            return f'{obj.file_size / 1024 / 1024:.2f} MB'
        return '-'
    file_size_mb.short_description = 'File Size'
    
    def duration(self, obj):
        if obj.download_duration:
            return f'{obj.download_duration:.2f}s'
        return '-'
    duration.short_description = 'Duration'


@admin.register(BotStatistics)
class BotStatisticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_requests', 'successful_downloads', 'failed_downloads', 
                   'success_rate', 'unique_users', 'data_transferred_mb']
    list_filter = ['date']
    readonly_fields = ['date', 'total_requests', 'successful_downloads', 'failed_downloads',
                      'unique_users', 'instagram_downloads', 'youtube_downloads', 
                      'twitter_downloads', 'total_data_transferred', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    def success_rate(self, obj):
        if obj.total_requests > 0:
            rate = (obj.successful_downloads / obj.total_requests) * 100
            color = 'green' if rate > 80 else 'orange' if rate > 50 else 'red'
            return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
        return '-'
    success_rate.short_description = 'Success Rate'
    
    def data_transferred_mb(self, obj):
        return f'{obj.total_data_transferred / 1024 / 1024:.2f} MB'
    data_transferred_mb.short_description = 'Data Transferred'


@admin.register(BotLog)
class BotLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'level_colored', 'message_short', 'user_link', 'url_link']
    list_filter = ['level', 'created_at']
    search_fields = ['message', 'user__username', 'url']
    readonly_fields = ['level', 'message', 'user', 'url', 'exception', 'metadata', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Log Information', {
            'fields': ('level', 'message', 'created_at')
        }),
        ('Context', {
            'fields': ('user', 'url')
        }),
        ('Error Details', {
            'fields': ('exception', 'metadata'),
            'classes': ('collapse',)
        }),
    )
    
    def level_colored(self, obj):
        colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.level, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.level.upper())
    level_colored.short_description = 'Level'
    
    def message_short(self, obj):
        return obj.message[:100] + ('...' if len(obj.message) > 100 else '')
    message_short.short_description = 'Message'
    
    def user_link(self, obj):
        if obj.user:
            return format_html('<a href="/admin/bot_app/telegramuser/{}/change/">{}</a>',
                             obj.user.id, obj.user.username or obj.user.telegram_id)
        return '-'
    user_link.short_description = 'User'
    
    def url_link(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">{}</a>', 
                             obj.url, obj.url[:50] + ('...' if len(obj.url) > 50 else ''))
        return '-'
    url_link.short_description = 'URL'
