"""
URL configuration for API endpoints
"""
from django.urls import path
from . import views, auth_views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.register, name='register'),
    path('auth/login/', auth_views.login, name='login'),
    path('auth/refresh/', auth_views.refresh_token, name='refresh_token'),
    
    # Free blog posts - accessible to everyone
    path('posts/free/', views.FreePostListView.as_view(), name='free_posts'),
    path('posts/free/<slug:slug>/', views.FreePostDetailView.as_view(), name='free_post_detail'),
    
    # Paid blog posts - content access controlled
    path('posts/paid/', views.PaidPostListView.as_view(), name='paid_posts'),
    path('posts/paid/<slug:slug>/', views.PaidPostDetailView.as_view(), name='paid_post_detail'),
    
    # All blog posts - mixed free and paid
    path('posts/', views.AllPostListView.as_view(), name='all_posts'),
    path('posts/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>/posts/', views.CategoryPostListView.as_view(), name='category_posts'),
    
    # Tags
    path('tags/', views.TagListView.as_view(), name='tags'),
    path('tags/<slug:slug>/posts/', views.TagPostListView.as_view(), name='tag_posts'),
    
    # Search and special endpoints
    path('posts/search/', views.post_search, name='post_search'),
    path('posts/featured/', views.featured_posts, name='featured_posts'),
    path('posts/latest/', views.latest_posts, name='latest_posts'),
    
    # User-specific endpoints (require authentication)
    path('user/check-access/', views.CheckPaidPostAccessView.as_view(), name='check_access'),
    path('user/purchased-posts/', views.UserPurchasedPostsView.as_view(), name='user_purchased_posts'),
]