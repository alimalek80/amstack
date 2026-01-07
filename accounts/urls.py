from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/saved-tutorials/', views.saved_tutorials_view, name='saved_tutorials'),
    path('dashboard/my-courses/', views.my_courses_view, name='my_courses'),
    path('dashboard/my-orders/', views.my_orders_view, name='my_orders'),
    path('dashboard/profile-settings/', views.profile_settings_view, name='profile_settings'),
    path('dashboard/newsletter/', views.newsletter_settings_view, name='newsletter_settings'),
]
