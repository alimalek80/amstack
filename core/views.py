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


def tools(request):
    """Tools hub page showing all available development tools."""
    tools_list = [
        {
            'name': 'Markdown Live Preview',
            'description': 'Write and preview Markdown in real-time with a side-by-side editor and live preview.',
            'icon': 'markdown',
            'url': 'tools:markdown_live_preview',
            'category': 'Text & Documentation',
            'featured': True,
            'tags': ['markdown', 'preview', 'editor', 'documentation']
        },
        # Future tools can be added here
        # {
        #     'name': 'JSON Formatter',
        #     'description': 'Format, validate and beautify JSON data.',
        #     'icon': 'code',
        #     'url': 'tools:json_formatter',
        #     'category': 'Data & Format',
        #     'featured': False,
        #     'tags': ['json', 'formatter', 'validator']
        # },
    ]
    
    context = {
        'tools': tools_list,
        'featured_tools': [tool for tool in tools_list if tool.get('featured', False)],
    }
    return render(request, 'core/tools.html', context)
