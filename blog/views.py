from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Post, Tag, Category, SavedPost
from orders.utils import user_has_post_access


def post_list(request):
    """List all published blog posts with search and filtering."""
    posts = Post.objects.filter(is_published=True)
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Filter by type
    post_type = request.GET.get('type', '')
    if post_type:
        posts = posts.filter(post_type=post_type)
    
    # Filter by category
    category_slug = request.GET.get('category', '')
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            # Include posts from this category and its subcategories
            category_ids = [current_category.id]
            category_ids.extend(current_category.subcategories.values_list('id', flat=True))
            posts = posts.filter(category_id__in=category_ids)
    
    # Filter by free/paid
    access = request.GET.get('access', '')
    if access == 'free':
        posts = posts.filter(is_free=True)
    elif access == 'paid':
        posts = posts.filter(is_free=False)
    
    # Featured posts
    featured_posts = Post.objects.filter(is_published=True, is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(posts, 9)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    # Get all tags for filter sidebar
    tags = Tag.objects.all()
    
    # Get parent categories with subcategories for sidebar
    categories = Category.get_parent_categories()
    
    # Get user's saved posts if authenticated
    saved_post_ids = []
    if request.user.is_authenticated:
        saved_post_ids = list(
            SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
        )
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'tags': tags,
        'categories': categories,
        'current_category': current_category,
        'query': query,
        'post_type': post_type,
        'access': access,
        'saved_post_ids': saved_post_ids,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Display a single blog post."""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    
    # Check if user has access to paid content
    has_access = user_has_post_access(request.user, post)
    is_saved = False
    
    if request.user.is_authenticated:
        # Check if post is saved
        is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()

    # Related posts (same tags, excluding current)
    related_posts = Post.objects.filter(
        is_published=True,
        tags__in=post.tags.all()
    ).exclude(id=post.id).distinct()[:3]

    context = {
        'post': post,
        'has_access': has_access,
        'is_saved': is_saved,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


def tag_posts(request, slug):
    """List posts filtered by tag."""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(is_published=True, tags=tag)
    
    # Pagination
    paginator = Paginator(posts, 9)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    # Get user's saved posts if authenticated
    saved_post_ids = []
    if request.user.is_authenticated:
        saved_post_ids = list(
            SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True)
        )
    
    context = {
        'tag': tag,
        'posts': posts,
        'saved_post_ids': saved_post_ids,
    }
    return render(request, 'blog/tag_posts.html', context)



@login_required
@require_POST
def toggle_save_post(request, post_id):
    """Toggle save/unsave a post (AJAX endpoint)."""
    post = get_object_or_404(Post, id=post_id)
    
    saved, created = SavedPost.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        # Already saved, so unsave it
        saved.delete()
        is_saved = False
    else:
        is_saved = True
    
    # Update user's saved count
    request.user.profile.saved_tutorials_count = SavedPost.objects.filter(
        user=request.user
    ).count()
    request.user.profile.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'saved': is_saved})
    
    return redirect(post.get_absolute_url())


