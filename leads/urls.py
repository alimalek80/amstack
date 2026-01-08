from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    # Public URLs
    path('hire/', views.LeadCreateView.as_view(), name='lead_create'),
    path('hire/success/', views.LeadSuccessView.as_view(), name='lead_success'),
    
    # Dashboard URLs
    path('dashboard/leads/', views.LeadListView.as_view(), name='lead_list'),
    path('dashboard/leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
]
