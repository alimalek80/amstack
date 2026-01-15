from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('save/<int:post_id>/', views.toggle_save_post, name='toggle_save'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
