# Admin Notification System

This document describes the admin notification system that sends email alerts to `amstack.box@gmail.com` for important events.

## Overview

The notification system automatically sends email notifications to the AMStack administrator when:
1. A new user registers on the platform
2. A user enrolls in a course (free or paid)

## Features

### 1. New User Registration Notifications

When a new user registers, an email is sent to the admin with:
- User's full name
- Email address
- Username
- Registration date and time
- Email verification status
- User ID
- Direct link to view user in admin panel

### 2. Course Enrollment Notifications

When a user enrolls in a course, an email is sent to the admin with:
- Course title
- Course type (free or paid)
- Course price (if paid)
- Total number of lessons
- Student's full name
- Student's email
- Enrollment date and time
- Current progress
- Direct links to:
  - View enrollment in admin panel
  - View course in admin panel
  - View student in admin panel

## Implementation Details

### Files Modified/Created

1. **`core/notification_service.py`** (NEW)
   - Contains `AdminNotificationService` class
   - Methods:
     - `send_new_user_registration_notification(user)`
     - `send_course_enrollment_notification(enrollment)`

2. **`accounts/views.py`**
   - Modified `RegisterView.form_valid()` to send admin notification after user registration

3. **`courses/views.py`**
   - Modified `enroll_course()` to send admin notification when user manually enrolls

4. **`orders/utils.py`**
   - Modified `ensure_course_enrollment()` to send admin notification when user is auto-enrolled after purchase

5. **`core/management/commands/test_notifications.py`** (NEW)
   - Management command for testing notifications

## Configuration

The admin email is configured in `core/notification_service.py`:
```python
ADMIN_EMAIL = 'amstack.box@gmail.com'
```

Email settings are configured via environment variables in `settings.py`:
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_SSL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

## Testing

Test the notification system using the management command:

```bash
# Test both notifications
python manage.py test_notifications

# Test only registration notification
python manage.py test_notifications --test-type=registration

# Test only enrollment notification
python manage.py test_notifications --test-type=enrollment
```

## Error Handling

- All notification sending is wrapped in try-except blocks
- Failed notifications are logged but don't interrupt user workflows
- Users are never shown errors related to admin notifications
- Errors are logged using Django's logging system

## Email Templates

Both notifications include:
- **HTML version**: Styled with colors, tables, and formatting
- **Plain text version**: Fallback for email clients that don't support HTML
- **Quick action links**: Direct links to admin panel for relevant resources

## Automatic Triggers

### User Registration
- Triggered in: `accounts/views.py` → `RegisterView.form_valid()`
- Timing: After user is created, after verification email is sent
- No user impact if notification fails

### Course Enrollment
- Triggered in multiple places:
  1. `courses/views.py` → `enroll_course()` (manual enrollment)
  2. `orders/utils.py` → `ensure_course_enrollment()` (auto-enrollment after purchase)
  3. `courses/views.py` → `course_detail()` (auto-enrollment for paid orders)
  4. `courses/views.py` → `lesson_detail()` (auto-enrollment for paid orders)
- Timing: After enrollment is created
- Only sent for NEW enrollments (not existing ones)

## Security Notes

- Admin email is hardcoded in the service (not in settings or environment)
- Emails are sent asynchronously and failures don't block user actions
- No sensitive information (passwords, payment details) is included in emails
- All URLs use `settings.SITE_URL` for proper domain configuration

## Future Enhancements

Potential improvements:
- Add more notification types (order placed, payment received, etc.)
- Support multiple admin emails
- Add admin preferences for which notifications to receive
- Create an admin dashboard to view notification history
- Add Slack/Discord webhook support
- Batch notifications for high-volume events
