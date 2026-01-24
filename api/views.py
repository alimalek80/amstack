"""
API Views for Blog Posts with access control
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from blog.models import Post, Category, Tag
from orders.models import Order
from .serializers import (
    PostListSerializer, PostDetailSerializer, FreePostSerializer,
    CategorySerializer, TagSerializer, PaidPostAccessSerializer,
    UserPostAccessSerializer
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the object.
        return obj.author == request.user


class FreePostListView(generics.ListAPIView):
    """
    List all free blog posts - accessible to everyone
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category', 'post_type', 'is_featured']
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'title', 'reading_time']
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            is_free=True
        ).select_related('author', 'category').prefetch_related('tags')


class FreePostDetailView(generics.RetrieveAPIView):
    """
    Retrieve a free blog post - accessible to everyone
    """
    serializer_class = FreePostSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            is_free=True
        ).select_related('author', 'category').prefetch_related('tags')


class PaidPostListView(generics.ListAPIView):
    """
    List all paid blog posts - accessible to everyone but content restricted
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category', 'post_type', 'price']
    search_fields = ['title', 'excerpt']
    ordering_fields = ['published_at', 'title', 'price', 'reading_time']
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            is_free=False
        ).select_related('author', 'category').prefetch_related('tags')


class PaidPostDetailView(generics.RetrieveAPIView):
    """
    Retrieve a paid blog post - content access controlled by payment status
    """
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            is_free=False
        ).select_related('author', 'category').prefetch_related('tags')


class AllPostListView(generics.ListAPIView):
    """
    List all blog posts (free and paid) - content access controlled
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['category', 'post_type', 'is_free', 'is_featured']
    search_fields = ['title', 'excerpt']
    ordering_fields = ['published_at', 'title', 'price', 'reading_time']
    ordering = ['-published_at']
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')


class PostDetailView(generics.RetrieveAPIView):
    """
    Retrieve any blog post by slug - content access controlled
    """
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(
            is_published=True
        ).select_related('author', 'category').prefetch_related('tags')


class CategoryListView(generics.ListAPIView):
    """
    List all active categories
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('subcategories')


class CategoryPostListView(generics.ListAPIView):
    """
    List posts in a specific category
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_slug = self.kwargs['slug']
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        
        # Get posts from this category and its subcategories
        category_ids = [category.id]
        if category.is_parent:
            category_ids.extend(category.subcategories.values_list('id', flat=True))
        
        return Post.objects.filter(
            is_published=True,
            category_id__in=category_ids
        ).select_related('author', 'category').prefetch_related('tags')


class TagListView(generics.ListAPIView):
    """
    List all tags
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Tag.objects.all()


class TagPostListView(generics.ListAPIView):
    """
    List posts with a specific tag
    """
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        tag_slug = self.kwargs['slug']
        tag = get_object_or_404(Tag, slug=tag_slug)
        
        return Post.objects.filter(
            is_published=True,
            tags=tag
        ).select_related('author', 'category').prefetch_related('tags')


class CheckPaidPostAccessView(APIView):
    """
    Check if authenticated user has access to a paid post
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PaidPostAccessSerializer(data=request.data)
        if serializer.is_valid():
            post_id = serializer.validated_data['post_id']
            
            try:
                post = Post.objects.get(id=post_id, is_published=True)
                
                # Check if user has purchased this post
                has_access = Order.objects.filter(
                    user=request.user,
                    post=post,
                    status='paid'
                ).exists()
                
                return Response({
                    'post_id': post_id,
                    'has_access': has_access,
                    'purchase_required': not has_access,
                    'price': post.price,
                    'title': post.title,
                    'slug': post.slug
                })
                
            except Post.DoesNotExist:
                return Response(
                    {'error': 'Post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPurchasedPostsView(generics.ListAPIView):
    """
    List all posts purchased by the authenticated user
    """
    serializer_class = UserPostAccessSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status='paid',
            post__isnull=False
        ).select_related('post').order_by('-paid_at')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_search(request):
    """
    Search posts by title, excerpt, or content
    """
    query = request.GET.get('q', '')
    post_type = request.GET.get('type', '')  # 'free', 'paid', or '' for all
    
    if not query:
        return Response({'results': []})
    
    # Base queryset
    posts = Post.objects.filter(is_published=True)
    
    # Filter by type
    if post_type == 'free':
        posts = posts.filter(is_free=True)
    elif post_type == 'paid':
        posts = posts.filter(is_free=False)
    
    # Search
    posts = posts.filter(
        Q(title__icontains=query) |
        Q(excerpt__icontains=query) |
        Q(content__icontains=query)
    ).select_related('author', 'category').prefetch_related('tags')[:20]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_posts(request):
    """
    Get featured posts
    """
    posts = Post.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('author', 'category').prefetch_related('tags')[:10]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def latest_posts(request):
    """
    Get latest posts
    """
    limit = int(request.GET.get('limit', 10))
    posts = Post.objects.filter(
        is_published=True
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')[:limit]
    
    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({'results': serializer.data})
