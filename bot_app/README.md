# Telegram Media Downloader Bot - Django Integration

A Django-integrated Telegram bot that downloads media from Instagram, YouTube Shorts, and Twitter/X. This bot uses webhooks instead of polling, making it suitable for deployment on cPanel and shared hosting environments.

## Features

- 📸 Download Instagram posts, reels, and images
- 🎥 Download YouTube Shorts
- 🐦 Download Twitter/X videos and images
- 📊 Track download statistics
- 👥 User management
- 📝 Comprehensive logging
- 🔒 Secure webhook implementation
- 🎯 Admin interface for monitoring

## Installation

### 1. Install Dependencies

```bash
pip install -r bot_app/requirements.txt
```

Required packages:
- `python-telegram-bot==20.7` - Telegram Bot API wrapper
- `yt-dlp>=2023.12.30` - Video/media downloader
- `requests>=2.31.0` - HTTP library

### 2. Run Migrations

```bash
python manage.py makemigrations bot_app
python manage.py migrate
```

### 3. Configure Environment Variables

Add these to your `.env` file or environment:

```bash
# Required: Your Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Required: Your public webhook URL (must be HTTPS)
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/bot/webhook/your-secret-token/

# Optional: Secret token for webhook security (recommended)
TELEGRAM_WEBHOOK_SECRET=your-random-secret-token-here
```

### 4. Set Up the Webhook

After deploying to your server with HTTPS enabled:

```bash
# Set the webhook
python manage.py set_webhook

# Or specify URL directly
python manage.py set_webhook --url https://yourdomain.com/bot/webhook/your-secret-token/

# Check webhook status
python manage.py webhook_info

# Remove webhook (if needed)
python manage.py remove_webhook
```

## Configuration

### Settings (amstack/settings.py)

The bot configuration is already added to your settings:

```python
# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_token_here')

# Webhook URL (must be HTTPS)
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')

# Webhook Secret Token (for security)
TELEGRAM_WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', 'your-secret-token-here')

# Max file size (45MB to stay under Telegram's 50MB limit)
TELEGRAM_MAX_FILE_SIZE = 45 * 1024 * 1024
```

### Security Best Practices

1. **Use HTTPS**: Telegram requires HTTPS for webhooks
2. **Secret Token**: Include a random secret token in your webhook URL
3. **Environment Variables**: Never commit tokens to version control
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse

## Webhook URL Structure

Your webhook URL should follow this pattern:

```
https://yourdomain.com/bot/webhook/{SECRET_TOKEN}/
```

Example:
```
https://example.com/bot/webhook/abc123xyz789/
```

The secret token prevents unauthorized access to your webhook endpoint.

## Usage

### For Users

1. Start the bot: `/start`
2. Get help: `/help`
3. Send a URL from:
   - Instagram: `https://instagram.com/reel/...` or `https://instagram.com/p/...`
   - YouTube: `https://youtube.com/shorts/...`
   - Twitter/X: `https://twitter.com/...` or `https://x.com/...`

### For Admins

Access the Django admin panel at `/admin/` to:

- View and manage users
- Monitor download requests
- Check statistics
- Review logs
- Block/unblock users

## Management Commands

```bash
# Set up webhook
python manage.py set_webhook

# Check webhook status
python manage.py webhook_info

# Remove webhook
python manage.py remove_webhook
```

## cPanel Deployment

### Prerequisites

1. Python 3.8+ installed on cPanel
2. SSL certificate (HTTPS required for Telegram webhooks)
3. Access to cPanel terminal or SSH

### Deployment Steps

1. **Upload your Django project** to cPanel

2. **Create virtual environment**:
   ```bash
   cd ~/projects/otherProjects/amstack
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r bot_app/requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Configure environment variables** in cPanel or `.env` file

7. **Set up webhook**:
   ```bash
   python manage.py set_webhook --url https://yourdomain.com/bot/webhook/your-secret/
   ```

8. **Configure your web server** (Apache/Nginx) to serve the Django application

### cPanel-Specific Notes

- Use webhooks only (polling doesn't work well on shared hosting)
- Ensure your Django app runs via WSGI (Passenger or mod_wsgi)
- Check that HTTPS is properly configured
- Monitor logs in `/path/to/project/django_errors.log`

## Testing

### Local Testing with ngrok (Development Only)

For local development, you can use ngrok to create a temporary HTTPS tunnel:

```bash
# Start ngrok
ngrok http 8000

# Copy the HTTPS URL and set webhook
python manage.py set_webhook --url https://your-ngrok-url.ngrok.io/bot/webhook/test-token/

# Run Django development server
python manage.py runserver
```

**Note**: Remember to remove the webhook when done:
```bash
python manage.py remove_webhook
```

## Monitoring

### Admin Dashboard

Navigate to `/admin/bot_app/` to view:

- **Telegram Users**: All users who have interacted with the bot
- **Download Requests**: All download attempts with status and errors
- **Bot Statistics**: Daily statistics (requests, success rate, data transferred)
- **Bot Logs**: Detailed event logs

### Logs

Application logs are stored in:
- Console output (development)
- `django_errors.log` (production)
- Database (BotLog model for important events)

## Troubleshooting

### Webhook Not Working

1. **Check webhook status**:
   ```bash
   python manage.py webhook_info
   ```

2. **Verify HTTPS**: Telegram requires HTTPS
   ```bash
   curl -I https://yourdomain.com/bot/webhook/token/
   ```

3. **Check logs**: Look for errors in Django logs and webhook info

4. **Test manually**: Send a POST request to your webhook URL

### Downloads Failing

1. **Check yt-dlp version**: Update to latest
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Review logs**: Check `BotLog` in admin panel

3. **Test URL manually**:
   ```python
   from bot_app.services import download_media, is_supported_url
   is_supported, platform = is_supported_url('your-url-here')
   ```

### File Size Issues

- Maximum file size is set to 45MB (Telegram limit is 50MB)
- Large files will be rejected with an error message
- Adjust `TELEGRAM_MAX_FILE_SIZE` if needed

## API Endpoints

### Webhook Endpoint
- **URL**: `/bot/webhook/<token>/`
- **Method**: POST
- **Description**: Receives updates from Telegram
- **Authentication**: Token in URL

### Webhook Info
- **URL**: `/bot/webhook-info/`
- **Method**: GET
- **Description**: Displays current webhook configuration
- **Response**: JSON with webhook details

## Database Models

### TelegramUser
Stores information about bot users

### DownloadRequest
Tracks all download requests with status and metrics

### BotStatistics
Stores daily aggregate statistics

### BotLog
Logs important bot events and errors

## Contributing

To modify the bot:

1. **Bot logic**: Edit `bot_app/services.py`
2. **Webhook handlers**: Edit `bot_app/views.py`
3. **Models**: Edit `bot_app/models.py`
4. **Admin interface**: Edit `bot_app/admin.py`

## License

This bot is part of your amstack Django project.

## Support

For issues or questions:
1. Check logs in admin panel
2. Review `django_errors.log`
3. Use `python manage.py webhook_info` to debug webhook issues

## Security Notes

⚠️ **Important**: 
- Keep your bot token secret
- Use a strong random secret for webhook URL
- Enable HTTPS (required)
- Consider implementing rate limiting
- Monitor the logs for suspicious activity
- Block abusive users via admin panel
