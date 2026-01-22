from django.contrib import admin

from .models import Course, Lesson, CourseEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'is_free', 'price', 'created_at')
    list_filter = ('is_published', 'is_free')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'meta_keywords', 'focus_keyword')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        ('SEO Optimization', {
            'fields': (
                'seo_title', 'meta_description', 'meta_keywords', 
                'focus_keyword', 'schema_type'
            ),
            'classes': ('collapse',),
            'description': 'SEO fields are optional. If empty, will fallback to main title/description.'
        }),
        ('Media', {
            'fields': ('cover_image', 'og_image_alt'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_free', 'price')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_published', 'is_free', 'order')
    list_filter = ('course', 'is_published', 'is_free')
    search_fields = ('title', 'excerpt', 'course__title', 'meta_keywords', 'focus_keyword')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('course', 'order')
    
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'slug', 'excerpt', 'content')
        }),
        ('SEO Optimization', {
            'fields': (
                'seo_title', 'meta_description', 'meta_keywords', 
                'focus_keyword'
            ),
            'classes': ('collapse',),
            'description': 'SEO fields are optional. If empty, will fallback to main title/excerpt.'
        }),
        ('Media', {
            'fields': ('cover_image', 'og_image_alt'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'is_free', 'order', 'reading_time_override')
        }),
    )


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'progress')
    search_fields = ('user__email', 'course__title')
    list_filter = ('course',)
