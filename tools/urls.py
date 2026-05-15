from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('markdown/', views.markdown_live_preview, name='markdown_live_preview'),
    path('api/markdown-preview/', views.markdown_preview_api, name='markdown_preview_api'),
    path('md-to-pdf/', views.md_to_pdf, name='md_to_pdf'),
]