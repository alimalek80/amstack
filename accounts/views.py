from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from courses.models import CourseEnrollment
from orders.models import Order


class RegisterView(CreateView):
    """User registration view."""
    
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully! Welcome to Amstack.')
        return redirect(self.success_url)


class CustomLoginView(LoginView):
    """Custom login view with email authentication."""
    
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


def logout_view(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def dashboard_view(request):
    """User dashboard/profile overview."""
    user = request.user
    profile = user.profile
    
    # Get real recent orders from database
    recent_orders = Order.objects.filter(
        user=user, 
        status=Order.STATUS_PAID
    ).select_related('post', 'course', 'service').order_by('-paid_at')[:3]
    
    # Get real courses in progress
    enrollments = CourseEnrollment.objects.filter(
        user=user
    ).select_related('course', 'last_lesson').order_by('-enrolled_at')[:2]
    
    courses_progress = []
    for enrollment in enrollments:
        # Calculate progress based on lessons in course
        total_lessons = enrollment.course.lessons.filter(is_published=True).count()
        if total_lessons > 0:
            progress = min(100, enrollment.progress)
        else:
            progress = 0
            
        courses_progress.append({
            'title': enrollment.course.title,
            'progress': progress,
            'enrollment': enrollment,
        })
    
    context = {
        'user': user,
        'profile': profile,
        'recent_orders': recent_orders,
        'courses_progress': courses_progress,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def saved_tutorials_view(request):
    """View saved tutorials."""
    from blog.models import SavedPost
    from django.core.paginator import Paginator
    
    # Get user's saved posts
    saved_posts_queryset = SavedPost.objects.filter(user=request.user).select_related('post').order_by('-saved_at')
    
    # Pagination
    paginator = Paginator(saved_posts_queryset, 12)
    page = request.GET.get('page', 1)
    saved_posts_page = paginator.get_page(page)
    
    context = {
        'user': request.user,
        'profile': request.user.profile,
        'saved_posts': saved_posts_page,
        'total_saved': paginator.count,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': saved_posts_page,
    }
    return render(request, 'accounts/saved_tutorials.html', context)


@login_required
def my_courses_view(request):
    """View enrolled courses."""
    enrollments = (
        CourseEnrollment.objects
        .filter(user=request.user)
        .select_related('course', 'last_lesson')
        .order_by('-enrolled_at')
    )
    return render(request, 'accounts/my_courses.html', {'enrollments': enrollments})


@login_required
def my_orders_view(request):
    """View order history."""
    from django.core.paginator import Paginator
    
    # Only show paid and failed orders (exclude pending to reduce clutter)
    orders = Order.objects.filter(
        user=request.user,
        status__in=[Order.STATUS_PAID, Order.STATUS_FAILED, Order.STATUS_REFUNDED]
    ).select_related('post', 'course', 'service').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)
    
    context = {
        'orders': orders_page,
        'total_orders': paginator.count,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required
def profile_settings_view(request):
    """Update profile settings."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            # Save user fields
            user = form.save()
            
            # Update profile fields
            profile = user.profile
            bio = request.POST.get('bio', '').strip()
            if len(bio) <= 500:  # Validate bio length
                profile.bio = bio
            else:
                messages.error(request, 'Bio must be 500 characters or less.')
                return render(request, 'accounts/profile_settings.html', {
                    'form': form,
                    'user': request.user,
                    'profile': request.user.profile
                })
            
            profile.newsletter_subscribed = request.POST.get('newsletter_subscribed') == 'on'
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
        'profile': request.user.profile
    }
    return render(request, 'accounts/profile_settings.html', context)


@login_required
def newsletter_settings_view(request):
    """Newsletter subscription settings."""
    if request.method == 'POST':
        profile = request.user.profile
        profile.newsletter_subscribed = request.POST.get('subscribed', False) == 'on'
        profile.save()
        messages.success(request, 'Newsletter preferences updated!')
        return redirect('accounts:newsletter_settings')
    
    return render(request, 'accounts/newsletter_settings.html')
