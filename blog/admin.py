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
    list_display = ('title', 'post_type', 'category', 'is_published', 'is_featured', 'is_free', 'price', 'published_at', 'reading_time')
    list_filter = ('is_published', 'is_featured', 'is_free', 'post_type', 'category', 'tags')
    list_editable = ('is_published', 'is_featured', 'is_free')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'excerpt', 'content', 'meta_keywords', 'focus_keyword')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('SEO Optimization', {
            'fields': (
                'seo_title', 'meta_description', 'meta_keywords', 
                'focus_keyword', 'canonical_url', 'schema_type'
            ),
            'classes': ('collapse',),
            'description': 'SEO fields are optional. If empty, will fallback to main title/excerpt.'
        }),
        ('Media', {
            'fields': ('cover_image', 'og_image_alt'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'is_featured', 'is_free', 'price', 'reading_time_override'),
            'description': 'Set price to 0.00 or leave empty for free content. Uncheck "Is free" to make it a paid post.'
        }),
        ('Organization', {
            'fields': ('post_type', 'category', 'tags', 'author')
        }),
    )
    
    class Media:
        js = ('admin/js/post_price_handler.js',)
    
    def save_model(self, request, obj, form, change):
        # Auto-set is_free based on price
        if obj.price and obj.price > 0:
            obj.is_free = False
        elif obj.price == 0 or obj.price is None:
            obj.is_free = True
            obj.price = 0.00
        super().save_model(request, obj, form, change)


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'post__title')
