from django.contrib import admin
from .models import Category, Tag, Post, SavedPost


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order', 'is_active', 'post_count')
    list_filter = ('is_active', 'parent')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('parent__name', 'order', 'name')
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'post_type', 'category', 'is_published', 'is_featured', 'is_free', 'published_at', 'reading_time')
    list_filter = ('is_published', 'is_featured', 'is_free', 'post_type', 'category', 'tags')
    list_editable = ('is_published', 'is_featured', 'is_free')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'excerpt', 'content')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('cover_image',),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'is_featured', 'is_free')
        }),
        ('Organization', {
            'fields': ('post_type', 'category', 'tags', 'author')
        }),
    )


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'post__title')
