from django.shortcuts import render
from blog.models import Post


def home(request):
    """Home page view."""
    # Get the 3 latest published blog posts
    latest_posts = Post.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    context = {
        'latest_posts': latest_posts,
    }
    return render(request, 'core/home.html', context)
