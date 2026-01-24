"""
Serializers for API endpoints
"""
from rest_framework import serializers
from blog.models import Post, Category, Tag
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    subcategories = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'subcategories', 'posts_count', 'is_active']
        
    def get_subcategories(self, obj):
        if obj.is_parent and obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []
        
    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color', 'posts_count']
        
    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for User model (as author)"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name']


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for Post list view - minimal fields for performance"""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    is_accessible = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'cover_image',
            'published_at', 'reading_time', 'is_featured', 'is_free', 'price',
            'post_type', 'category', 'tags', 'author', 'is_accessible'
        ]
    
    def get_is_accessible(self, obj):
        """Check if user can access this post"""
        request = self.context.get('request')
        if not request:
            return obj.is_free
            
        # If post is free, everyone can access
        if obj.is_free:
            return True
            
        # If user is not authenticated, only free posts
        if not request.user.is_authenticated:
            return False
            
        # Check if user has paid for this post
        return Order.objects.filter(
            user=request.user,
            post=obj,
            status='paid'
        ).exists()


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for Post detail view"""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    reading_time = serializers.ReadOnlyField()
    get_seo_title = serializers.ReadOnlyField()
    get_meta_description = serializers.ReadOnlyField()
    get_keywords_list = serializers.ReadOnlyField()
    content = serializers.SerializerMethodField()
    is_accessible = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'cover_image',
            'published_at', 'updated_at', 'reading_time', 'is_featured',
            'is_free', 'price', 'post_type', 'category', 'tags', 'author',
            'get_seo_title', 'get_meta_description', 'get_keywords_list',
            'is_accessible'
        ]
    
    def get_content(self, obj):
        """Return content only if user has access"""
        request = self.context.get('request')
        
        # If post is free, return content
        if obj.is_free:
            return obj.content
            
        # If user is not authenticated, return None
        if not request or not request.user.is_authenticated:
            return None
            
        # Check if user has paid for this post
        has_access = Order.objects.filter(
            user=request.user,
            post=obj,
            status='paid'
        ).exists()
        
        if has_access:
            return obj.content
        else:
            # Return a teaser (first 500 characters)
            return obj.content[:500] + "... [Content locked - Purchase required]"
    
    def get_is_accessible(self, obj):
        """Check if user can access this post"""
        request = self.context.get('request')
        if not request:
            return obj.is_free
            
        # If post is free, everyone can access
        if obj.is_free:
            return True
            
        # If user is not authenticated, only free posts
        if not request.user.is_authenticated:
            return False
            
        # Check if user has paid for this post
        return Order.objects.filter(
            user=request.user,
            post=obj,
            status='paid'
        ).exists()


class FreePostSerializer(PostDetailSerializer):
    """Serializer for free posts - always returns full content"""
    
    def get_content(self, obj):
        """Always return content for free posts"""
        return obj.content


class PaidPostAccessSerializer(serializers.Serializer):
    """Serializer to check paid post access"""
    post_id = serializers.IntegerField()
    has_access = serializers.BooleanField(read_only=True)
    purchase_required = serializers.BooleanField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    def validate_post_id(self, value):
        """Validate that post exists and is not free"""
        try:
            post = Post.objects.get(id=value, is_published=True)
            if post.is_free:
                raise serializers.ValidationError("This post is free and doesn't require purchase")
            return value
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found")


class UserPostAccessSerializer(serializers.ModelSerializer):
    """Serializer for user's purchased posts"""
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_slug = serializers.CharField(source='post.slug', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'post_title', 'post_slug', 'paid_at', 'total_amount']