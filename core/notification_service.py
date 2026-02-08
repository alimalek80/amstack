"""
Notification service for sending admin notifications.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# Admin email for notifications
ADMIN_EMAIL = 'amstack.box@gmail.com'


class AdminNotificationService:
    """Service for sending notifications to admin."""
    
    @staticmethod
    def send_new_user_registration_notification(user):
        """
        Send notification to admin when a new user registers.
        
        Args:
            user: The newly registered user object
        """
        try:
            subject = f"🎉 New User Registration - {user.full_name or user.email}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4F46E5; border-bottom: 2px solid #4F46E5; padding-bottom: 10px;">
                            New User Registration
                        </h2>
                        
                        <div style="background-color: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #374151;">User Details:</h3>
                            
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Full Name:</td>
                                    <td style="padding: 8px 0;">{user.full_name or 'Not provided'}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Email:</td>
                                    <td style="padding: 8px 0;">{user.email}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Date Joined:</td>
                                    <td style="padding: 8px 0;">{user.date_joined.strftime('%B %d, %Y at %I:%M %p')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Email Verified:</td>
                                    <td style="padding: 8px 0;">
                                        {'✅ Yes' if user.email_verified else '❌ No (pending)'}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">User ID:</td>
                                    <td style="padding: 8px 0;">{user.id}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #4F46E5; margin: 20px 0;">
                            <p style="margin: 0; color: #1e40af;">
                                <strong>Quick Actions:</strong>
                            </p>
                            <p style="margin: 5px 0 0 0;">
                                <a href="{settings.SITE_URL}/admin/accounts/user/{user.id}/change/" 
                                   style="color: #4F46E5; text-decoration: none;">
                                    → View user in admin panel
                                </a>
                            </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            This is an automated notification from AMStack
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_content = f"""
New User Registration

User Details:
- Full Name: {user.full_name or 'Not provided'}
- Email: {user.email}
- Date Joined: {user.date_joined.strftime('%B %d, %Y at %I:%M %p')}
- Email Verified: {'Yes' if user.email_verified else 'No (pending)'}
- User ID: {user.id}

Quick Actions:
View user in admin panel: {settings.SITE_URL}/admin/accounts/user/{user.id}/change/

---
This is an automated notification from AMStack
            """
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ADMIN_EMAIL],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"Admin notification sent for new user registration: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for new user {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_course_enrollment_notification(enrollment):
        """
        Send notification to admin when a user enrolls in a course.
        
        Args:
            enrollment: The CourseEnrollment object
        """
        try:
            user = enrollment.user
            course = enrollment.course
            
            subject = f"📚 New Course Enrollment - {user.full_name or user.email} enrolled in {course.title}"
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 10px;">
                            New Course Enrollment
                        </h2>
                        
                        <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #374151;">Course Information:</h3>
                            
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Course:</td>
                                    <td style="padding: 8px 0;">{course.title}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Course Type:</td>
                                    <td style="padding: 8px 0;">
                                        {'🆓 Free Course' if course.is_free else f'💰 Paid Course (${course.price})'}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Total Lessons:</td>
                                    <td style="padding: 8px 0;">{course.total_lessons}</td>
                                </tr>
                            </table>
                            
                            <h3 style="margin-top: 20px; color: #374151;">Student Information:</h3>
                            
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Student Name:</td>
                                    <td style="padding: 8px 0;">{user.full_name or 'Not provided'}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Email:</td>
                                    <td style="padding: 8px 0;">{user.email}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Enrollment Date:</td>
                                    <td style="padding: 8px 0;">{enrollment.enrolled_at.strftime('%B %d, %Y at %I:%M %p')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #6b7280;">Current Progress:</td>
                                    <td style="padding: 8px 0;">{enrollment.progress}%</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="background-color: #eff6ff; padding: 15px; border-left: 4px solid #10b981; margin: 20px 0;">
                            <p style="margin: 0; color: #1e40af;">
                                <strong>Quick Actions:</strong>
                            </p>
                            <p style="margin: 5px 0 0 0;">
                                <a href="{settings.SITE_URL}/admin/courses/courseenrollment/{enrollment.id}/change/" 
                                   style="color: #10b981; text-decoration: none;">
                                    → View enrollment in admin panel
                                </a>
                            </p>
                            <p style="margin: 5px 0 0 0;">
                                <a href="{settings.SITE_URL}/admin/courses/course/{course.id}/change/" 
                                   style="color: #10b981; text-decoration: none;">
                                    → View course in admin panel
                                </a>
                            </p>
                            <p style="margin: 5px 0 0 0;">
                                <a href="{settings.SITE_URL}/admin/accounts/user/{user.id}/change/" 
                                   style="color: #10b981; text-decoration: none;">
                                    → View student in admin panel
                                </a>
                            </p>
                        </div>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 12px; text-align: center;">
                            This is an automated notification from AMStack
                        </p>
                    </div>
                </body>
            </html>
            """
            
            text_content = f"""
New Course Enrollment

Course Information:
- Course: {course.title}
- Course Type: {'Free Course' if course.is_free else f'Paid Course (${course.price})'}
- Total Lessons: {course.total_lessons}

Student Information:
- Student Name: {user.full_name or 'Not provided'}
- Email: {user.email}
- Enrollment Date: {enrollment.enrolled_at.strftime('%B %d, %Y at %I:%M %p')}
- Current Progress: {enrollment.progress}%

Quick Actions:
View enrollment: {settings.SITE_URL}/admin/courses/courseenrollment/{enrollment.id}/change/
View course: {settings.SITE_URL}/admin/courses/course/{course.id}/change/
View student: {settings.SITE_URL}/admin/accounts/user/{user.id}/change/

---
This is an automated notification from AMStack
            """
            
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ADMIN_EMAIL],
                html_message=html_content,
                fail_silently=False,
            )
            
            logger.info(f"Admin notification sent for course enrollment: {user.email} -> {course.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for enrollment {enrollment.id}: {str(e)}")
            return False
