from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('save/<int:post_id>/', views.toggle_save_post, name='toggle_save'),
    path('comment/add/<slug:slug>/', views.add_comment, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('rate/<slug:slug>/', views.rate_post, name='rate_post'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
