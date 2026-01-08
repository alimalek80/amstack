from django.contrib import admin
from django.utils.html import format_html
from .models import Lead


@admin.action(description="Mark selected as Contacted")
def mark_contacted(modeladmin, request, queryset):
    queryset.update(status='contacted')


@admin.action(description="Mark selected as Qualified")
def mark_qualified(modeladmin, request, queryset):
    queryset.update(status='qualified')


@admin.action(description="Mark selected as Won")
def mark_won(modeladmin, request, queryset):
    queryset.update(status='won')


@admin.action(description="Mark selected as Lost")
def mark_lost(modeladmin, request, queryset):
    queryset.update(status='lost')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'service_display', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at', 'source')
    search_fields = ('full_name', 'email', 'phone', 'company', 'service_slug', 'service_title', 'message')
    readonly_fields = ('created_at', 'updated_at', 'service_slug', 'source')
    ordering = ('-created_at',)
    actions = [mark_contacted, mark_qualified, mark_won, mark_lost]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone', 'company')
        }),
        ('Project Details', {
            'fields': ('service_slug', 'service_title', 'budget', 'timeline', 'message')
        }),
        ('Lead Status', {
            'fields': ('status', 'source')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def service_display(self, obj):
        """Display service title or slug."""
        if obj.service_title:
            return obj.service_title
        elif obj.service_slug:
            return f"({obj.service_slug})"
        return "-"
    service_display.short_description = 'Service'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        status_colors = {
            'new': '#FF6B6B',
            'contacted': '#4ECDC4',
            'qualified': '#45B7D1',
            'won': '#51CF66',
            'lost': '#868E96',
        }
        color = status_colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

