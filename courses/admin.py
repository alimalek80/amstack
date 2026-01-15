from django.contrib import admin

from .models import Course, Lesson, CourseEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'is_free', 'price', 'created_at')
    list_filter = ('is_published', 'is_free')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_published', 'is_free', 'order')
    list_filter = ('course', 'is_published', 'is_free')
    search_fields = ('title', 'excerpt', 'course__title')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('course', 'order')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'progress')
    search_fields = ('user__email', 'course__title')
    list_filter = ('course',)
