# Email Verification Setup Guide

## Overview
The AMStack application now includes email verification for new user registrations. Users must verify their email address before they can log in.

## How It Works

1. **User Registration**: When a user registers, they receive a verification email at the provided email address.
2. **Email Verification**: The user clicks the verification link in the email.
3. **Account Activation**: Once verified, the user's account is activated and they can log in.

## Email Configuration

### Production Settings (SSL/TLS - Recommended)

Add the following environment variables to your production server:

```bash
# Email Settings for production
EMAIL_HOST=amstack.org
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=noreply@amstack.org
EMAIL_HOST_PASSWORD=your_actual_email_password
DEFAULT_FROM_EMAIL=AMStack <noreply@amstack.org>
SITE_URL=https://amstack.org
```

### Email Server Details

**Outgoing Mail Server (SMTP)**:
- Server: `amstack.org`
- Port: `465` (SSL)
- Username: `noreply@amstack.org`
- Password: Your email account password
- Authentication: Required
- SSL/TLS: Enabled

### Alternative Non-SSL Settings (Not Recommended)

If you need to use non-SSL settings:

```bash
EMAIL_HOST=mail.amstack.org
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_HOST_USER=noreply@amstack.org
EMAIL_HOST_PASSWORD=your_actual_email_password
```

## Development Mode

In development (`DEBUG=True`), emails are printed to the console instead of being sent. This is useful for testing without actually sending emails.

## Features Implemented

### 1. Email Verification on Registration
- New users receive a verification email immediately after registration
- Users cannot log in until their email is verified
- The verification link expires based on Django's token timeout

### 2. Resend Verification Email
- Users can request a new verification email if they didn't receive it
- Available at: `/accounts/resend-verification/`
- Link provided on the login page

### 3. Email Templates
- Professional HTML email templates with branding
- Fallback plain text versions
- Clear call-to-action buttons

### 4. Security Features
- Secure token generation using Django's default token generator
- Base64 encoded user IDs in verification URLs
- Accounts remain inactive until verification

## Database Changes

### New Fields in User Model
- `email_verified` (BooleanField): Tracks whether email is verified
- `is_active` (BooleanField): Changed default to `False` (activated upon verification)

### Migrations
Three migrations were created:
1. `0002_user_email_verified_alter_user_is_active.py` - Adds email_verified field
2. `0003_set_existing_users_verified.py` - Sets existing users as verified

## URLs

New URL patterns added:
- `/accounts/verify-email/<uidb64>/<token>/` - Email verification endpoint
- `/accounts/resend-verification/` - Resend verification email page

## Testing

### Test in Development Mode

1. Register a new account
2. Check the console/terminal for the verification email
3. Copy the verification URL from the console
4. Visit the URL in your browser
5. Verify that you can now log in

### Test in Production

1. Set up environment variables with actual email credentials
2. Register a new account with a real email address
3. Check your email inbox
4. Click the verification link
5. Log in to your account

## Troubleshooting

### Users Can't Receive Emails

1. **Check email credentials**: Ensure `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are correct
2. **Check SMTP settings**: Verify `EMAIL_HOST` and `EMAIL_PORT` are correct
3. **Check spam folder**: Verification emails might be marked as spam
4. **Check server firewall**: Ensure port 465 (or 587) is not blocked
5. **Check Django logs**: Look for email sending errors in `django_errors.log`

### Verification Link Doesn't Work

1. **Link expired**: Token has a timeout - use resend verification
2. **Site URL incorrect**: Check `SITE_URL` environment variable
3. **User already verified**: Check user's `email_verified` status in admin

### Existing Users Can't Log In

The migration `0003_set_existing_users_verified.py` should have marked all existing users as verified. If not, run:

```bash
python manage.py shell
```

Then execute:
```python
from accounts.models import User
User.objects.all().update(email_verified=True, is_active=True)
```

## Admin Panel

Admins can manually verify users through the Django admin panel:
1. Go to `/admin/accounts/user/`
2. Select the user
3. Check `email_verified` and `is_active` boxes
4. Save

## Future Enhancements

Consider adding:
- Email verification reminders after X days
- Password reset via email
- Email change verification
- Two-factor authentication via email
- Configurable token expiration time

## Security Notes

- Always use SSL/TLS (port 465) in production
- Keep `EMAIL_HOST_PASSWORD` secret and never commit it to version control
- Use environment variables for all sensitive configuration
- Consider rate limiting for resend verification requests
- Monitor for abuse of the registration system

## Support

For issues or questions, check:
- Django logs: `django_errors.log`
- Email backend configuration in `settings.py`
- Environment variables in `.env` file
