from django.contrib import admin
from django.utils.text import slugify
from .models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'pricing_type', 'starting_price', 'fixed_price', 'is_active', 'is_featured', 'category']
    list_filter = ['is_active', 'is_featured', 'pricing_type', 'category']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'starting_price', 'fixed_price'),
            'classes': ('collapse',)
        }),
        ('Service Details', {
            'fields': ('timeline', 'deliverables', 'requirements', 'faqs'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
