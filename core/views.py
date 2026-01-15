from django.shortcuts import render
from blog.models import Post
from courses.models import Course


def home(request):
    """Home page view."""
    # Get featured and latest published blog posts
    featured_posts = Post.objects.filter(
        is_published=True,
        is_featured=True
    ).order_by('-published_at')[:3]
    
    latest_posts = Post.objects.filter(
        is_published=True
    ).order_by('-published_at')[:6]
    
    # Get published courses
    featured_courses = Course.objects.filter(
        is_published=True
    ).order_by('-created_at')[:3]
    
    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'featured_courses': featured_courses,
    }
    return render(request, 'core/home.html', context)
