from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from courses.models import CourseEnrollment
from orders.models import Order

User = get_user_model()


class RegisterView(CreateView):
    """User registration view."""
    
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        
        # Send verification email
        try:
            self.send_verification_email(user)
            messages.success(
                self.request, 
                'Account created successfully! Please check your email to verify your account.'
            )
        except Exception as e:
            # Log the error and show a user-friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send verification email to {user.email}: {str(e)}')
            messages.warning(
                self.request, 
                f'Account created but we could not send the verification email. Error: {str(e)}. Please try resending it.'
            )
        
        return redirect(self.success_url)
    
    def send_verification_email(self, user):
        """Send email verification link to user."""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_url = f"{settings.SITE_URL}/accounts/verify-email/{uid}/{token}/"
        
        subject = 'Verify your AMStack account'
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Welcome to AMStack!</h2>
                    <p>Hi {user.full_name or 'there'},</p>
                    <p>Thank you for registering with AMStack. Please verify your email address by clicking the button below:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #4F46E5;">{verification_url}</p>
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        If you didn't create an account with AMStack, please ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        (c) 2026 AMStack. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )


class CustomLoginView(LoginView):
    """Custom login view with email authentication."""
    
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        # Check if user's email is verified
        user = form.get_user()
        if not user.email_verified:
            messages.error(
                self.request, 
                'Please verify your email address before logging in. Check your inbox for the verification link.'
            )
            return redirect('accounts:login')
        
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


def verify_email(request, uidb64, token):
    """Verify user email address."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('core:home')


def resend_verification_email(request):
    """Resend verification email to user."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, email_verified=False)
            
            # Generate new token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            verification_url = f"{settings.SITE_URL}/accounts/verify-email/{uid}/{token}/"
            
            subject = 'Verify your AMStack account'
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4F46E5;">Welcome to AMStack!</h2>
                        <p>Hi {user.full_name or 'there'},</p>
                        <p>Please verify your email address by clicking the button below:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" 
                               style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Verify Email Address
                            </a>
                        </div>
                        <p>Or copy and paste this link in your browser:</p>
                        <p style="word-break: break-all; color: #4F46E5;">{verification_url}</p>
                        <p style="margin-top: 30px; color: #666; font-size: 14px;">
                            If you didn't create an account with AMStack, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            (c) 2026 AMStack. All rights reserved.
                        </p>
                    </div>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, 'Verification email sent! Please check your inbox.')
        except User.DoesNotExist:
            messages.error(request, 'No unverified account found with that email address.')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send verification email to {email}: {str(e)}')
            messages.error(request, f'Failed to send email. Error: {str(e)}. Please contact support.')
        
        return redirect('accounts:login')
    
    return render(request, 'accounts/resend_verification.html')
