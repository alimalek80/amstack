from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm


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
    
    # Demo data for recent orders (will be replaced with real data later)
    recent_orders = [
        {'id': 'ORD-2024-002', 'item': 'Production-Grade Django + Tailwind SaaS', 'status': 'Paid'},
        {'id': 'ORD-2024-004', 'item': 'Celery Task Queues Bundle', 'status': 'Paid'},
        {'id': 'ORD-2024-006', 'item': 'PostgreSQL Optimization', 'status': 'Paid'},
    ]
    
    # Demo data for courses in progress
    courses_progress = [
        {'title': 'Production-Grade Django + Tailwind SaaS Architecture', 'progress': 60},
        {'title': 'PostgreSQL Optimization for Django Apps', 'progress': 25},
    ]
    
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
    return render(request, 'accounts/saved_tutorials.html')


@login_required
def my_courses_view(request):
    """View enrolled courses."""
    return render(request, 'accounts/my_courses.html')


@login_required
def my_orders_view(request):
    """View order history."""
    return render(request, 'accounts/my_orders.html')


@login_required
def profile_settings_view(request):
    """Update profile settings."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Update profile fields
            profile = request.user.profile
            profile.bio = request.POST.get('bio', '')
            profile.newsletter_subscribed = request.POST.get('newsletter_subscribed', False) == 'on'
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile_settings.html', {'form': form})


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
