from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError
import logging

from .models import Post, Tag, Category, SavedPost
from orders.utils import user_has_post_access

logger = logging.getLogger('blog')


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
    try:
        logger.debug(f"Accessing post detail for slug: {slug}")
        
        post = get_object_or_404(Post, slug=slug, is_published=True)
        
        # Check if user has access to paid content
        has_access = user_has_post_access(request.user, post)
        is_saved = False
        
        if request.user.is_authenticated:
            try:
                # Check if post is saved
                is_saved = SavedPost.objects.filter(user=request.user, post=post).exists()
                logger.debug(f"Post {slug} save status for user {request.user.email}: {is_saved}")
            except Exception as e:
                logger.error(f"Error checking saved status for post {slug}, user {request.user.email}: {str(e)}")
                # Continue without failing the whole view
                is_saved = False

        # Related posts (same tags, excluding current)
        try:
            related_posts = Post.objects.filter(
                is_published=True,
                tags__in=post.tags.all()
            ).exclude(id=post.id).distinct()[:3]
            logger.debug(f"Found {len(related_posts)} related posts for {slug}")
        except Exception as e:
            logger.error(f"Error fetching related posts for {slug}: {str(e)}")
            related_posts = []

        context = {
            'post': post,
            'has_access': has_access,
            'is_saved': is_saved,
            'related_posts': related_posts,
        }
        
        logger.debug(f"Successfully rendered post detail for {slug}")
        return render(request, 'blog/post_detail.html', context)
        
    except Exception as e:
        logger.error(f"Unexpected error in post_detail for slug {slug}: {str(e)}")
        logger.exception("Full traceback:")
        messages.error(request, "An error occurred while loading the post.")
        return redirect('blog:post_list')

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
    try:
        logger.debug(f"User {request.user.email} attempting to toggle save for post {post_id}")
        
        post = get_object_or_404(Post, id=post_id)
        
        # Check if user has a profile
        if not hasattr(request.user, 'profile'):
            logger.error(f"User {request.user.email} has no profile - this should not happen")
            messages.error(request, "Profile error. Please contact support.")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Profile not found'}, status=400)
            return redirect(post.get_absolute_url())
        
        saved, created = SavedPost.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            # Already saved, so unsave it
            saved.delete()
            is_saved = False
            logger.debug(f"Post {post_id} unsaved by user {request.user.email}")
        else:
            is_saved = True
            logger.debug(f"Post {post_id} saved by user {request.user.email}")
        
        # Update user's saved count
        try:
            saved_count = SavedPost.objects.filter(user=request.user).count()
            request.user.profile.saved_tutorials_count = saved_count
            request.user.profile.save()
            logger.debug(f"Updated saved count for user {request.user.email}: {saved_count}")
        except Exception as e:
            logger.error(f"Failed to update saved count for user {request.user.email}: {str(e)}")
            # Don't fail the whole operation for this
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'saved': is_saved})
        
        messages.success(request, f"Post {'saved' if is_saved else 'removed from saved'}")
        return redirect(post.get_absolute_url())
        
    except Post.DoesNotExist:
        logger.error(f"User {request.user.email} tried to save non-existent post {post_id}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Post not found'}, status=404)
        messages.error(request, "Post not found.")
        return redirect('blog:post_list')
        
    except Exception as e:
        logger.error(f"Unexpected error in toggle_save_post for user {request.user.email}, post {post_id}: {str(e)}")
        logger.exception("Full traceback:")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
        
        messages.error(request, "An error occurred. Please try again.")
        try:
            post = Post.objects.get(id=post_id)
            return redirect(post.get_absolute_url())
        except Post.DoesNotExist:
            return redirect('blog:post_list')


