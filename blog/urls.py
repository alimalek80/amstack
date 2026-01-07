from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('save/<int:post_id>/', views.toggle_save_post, name='toggle_save'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
