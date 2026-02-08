"""
Management command to test admin notification emails.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, CourseEnrollment
from core.notification_service import AdminNotificationService

User = get_user_model()


class Command(BaseCommand):
    help = 'Test admin notification emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['registration', 'enrollment', 'both'],
            default='both',
            help='Type of notification to test'
        )

    def handle(self, *args, **options):
        test_type = options['test_type']
        
        if test_type in ['registration', 'both']:
            self.test_registration_notification()
        
        if test_type in ['enrollment', 'both']:
            self.test_enrollment_notification()

    def test_registration_notification(self):
        """Test new user registration notification."""
        self.stdout.write(self.style.WARNING('\nTesting user registration notification...'))
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'full_name': 'Test User',
                'email_verified': True,
                'is_active': True,
            }
        )
        
        if not created:
            self.stdout.write(self.style.NOTICE(f'Using existing test user: {user.email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created test user: {user.email}'))
        
        # Send notification
        success = AdminNotificationService.send_new_user_registration_notification(user)
        
        if success:
            self.stdout.write(self.style.SUCCESS('✅ Registration notification sent successfully!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send registration notification'))

    def test_enrollment_notification(self):
        """Test course enrollment notification."""
        self.stdout.write(self.style.WARNING('\nTesting course enrollment notification...'))
        
        # Get or create a test user
        user, _ = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'full_name': 'Test User',
                'email_verified': True,
                'is_active': True,
            }
        )
        
        # Get or create a test course
        course = Course.objects.filter(is_published=True).first()
        
        if not course:
            self.stdout.write(self.style.ERROR('❌ No published courses found. Please create a course first.'))
            return
        
        self.stdout.write(self.style.NOTICE(f'Using course: {course.title}'))
        
        # Create enrollment
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=user,
            course=course
        )
        
        if not created:
            self.stdout.write(self.style.NOTICE(f'Using existing enrollment'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created test enrollment'))
        
        # Send notification
        success = AdminNotificationService.send_course_enrollment_notification(enrollment)
        
        if success:
            self.stdout.write(self.style.SUCCESS('✅ Enrollment notification sent successfully!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Failed to send enrollment notification'))
        
        self.stdout.write(self.style.SUCCESS('\n✨ Test completed!'))
