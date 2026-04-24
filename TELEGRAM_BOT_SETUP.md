# Quick Setup Guide for Telegram Bot

## ✅ Installation Complete!

Your Telegram bot has been successfully integrated into your Django project. Here's what was created:

### 📁 Files Created
- `bot_app/models.py` - Database models for users, downloads, stats, and logs
- `bot_app/services.py` - Media download logic (Instagram, YouTube, Twitter/X)
- `bot_app/views.py` - Webhook handlers
- `bot_app/urls.py` - URL routing
- `bot_app/admin.py` - Admin interface
- `bot_app/management/commands/` - Management commands (set_webhook, remove_webhook, webhook_info)
- `bot_app/README.md` - Full documentation
- `bot_app/requirements.txt` - Python dependencies

### ⚙️ Configuration Added
- Bot settings in `amstack/settings.py`
- Logging configuration for bot_app
- URL routing in main `amstack/urls.py`

### 🗄️ Database
- ✅ Migrations created and applied
- ✅ Tables created: bot_telegram_users, bot_download_requests, bot_statistics, bot_logs

---

## 🚀 Next Steps for cPanel Deployment

### 1. Update Your Telegram Bot Token

Edit your `.env` file or add to cPanel environment variables:

```bash
TELEGRAM_BOT_TOKEN=8339817857:AAGjAOrbww0wgqFifxsc7jSH3c0ZWjNd8lk
```

### 2. Generate a Secret Token

For security, generate a random secret token:

```bash
# On Linux/Mac:
openssl rand -hex 32

# Or use Python:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add it to your `.env`:
```bash
TELEGRAM_WEBHOOK_SECRET=your-generated-secret-token-here
```

### 3. Deploy to cPanel

Once your site is live with HTTPS:

```bash
# Set webhook (use your actual domain and secret token)
python manage.py set_webhook --url https://yourdomain.com/bot/webhook/your-secret-token/

# Verify webhook is set
python manage.py webhook_info
```

### 4. Test Your Bot

1. Open Telegram
2. Search for your bot by username (get from @BotFather)
3. Send `/start`
4. Send an Instagram, YouTube, or Twitter link

---

## 📊 Admin Panel

Access at: `https://yourdomain.com/admin/bot_app/`

You can:
- View all users
- Monitor download requests
- Check daily statistics
- Review logs
- Block/unblock users

---

## 🔧 Important Settings

### In `amstack/settings.py`:

```python
# Your bot token (keep secret!)
TELEGRAM_BOT_TOKEN = '8339817857:AAGjAOrbww0wgqFifxsc7jSH3c0ZWjNd8lk'

# Webhook URL (set after deployment)
TELEGRAM_WEBHOOK_URL = 'https://yourdomain.com/bot/webhook/YOUR_SECRET/'

# Secret token for security
TELEGRAM_WEBHOOK_SECRET = 'your-random-secret'
```

### Webhook URL Format:

**✅ Correct**: `https://yourdomain.com/bot/webhook/abc123xyz789/`

**❌ Wrong**: 
- `http://...` (must be HTTPS)
- Missing secret token
- No trailing slash

---

## 🧪 Testing Locally (Development)

For local development, use ngrok:

```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Set webhook with ngrok URL
python manage.py set_webhook --url https://YOUR-NGROK-URL.ngrok.io/bot/webhook/test-token/

# Terminal 3: Run Django
python manage.py runserver

# When done, remove webhook:
python manage.py remove_webhook
```

---

## 📝 Management Commands

```bash
# Set webhook
python manage.py set_webhook

# Check webhook status
python manage.py webhook_info

# Remove webhook (useful when switching from polling to webhook)
python manage.py remove_webhook
```

---

## 🐛 Troubleshooting

### "Webhook not receiving updates"

1. Check webhook status:
   ```bash
   python manage.py webhook_info
   ```

2. Verify HTTPS is working:
   ```bash
   curl -I https://yourdomain.com
   ```

3. Check Django logs:
   ```bash
   tail -f django_errors.log
   ```

### "ModuleNotFoundError"

Install dependencies:
```bash
pip install -r bot_app/requirements.txt
```

### "Downloads failing"

Update yt-dlp:
```bash
pip install --upgrade yt-dlp
```

---

## 📦 Required Python Packages

Already installed in your virtual environment:
- `python-telegram-bot==20.7`
- `yt-dlp` (latest)
- `requests`

---

## 🔐 Security Checklist

- [x] Use HTTPS (required by Telegram)
- [ ] Set strong secret token in webhook URL
- [ ] Never commit `.env` file to git
- [ ] Keep `TELEGRAM_BOT_TOKEN` secret
- [ ] Monitor logs for abuse
- [ ] Use admin panel to block abusive users

---

## 📚 Full Documentation

See `bot_app/README.md` for complete documentation including:
- Detailed deployment guide
- API endpoints
- Database models
- Contributing guidelines

---

## ✨ Features

✅ Download from Instagram, YouTube Shorts, Twitter/X  
✅ Supports both images and videos  
✅ Webhook-based (cPanel compatible)  
✅ User tracking and statistics  
✅ Comprehensive logging  
✅ Admin dashboard  
✅ Error handling and retries  
✅ File size validation  

---

## 💡 Tips

1. **Start with ngrok testing** before deploying to cPanel
2. **Check webhook_info regularly** to monitor errors
3. **Use admin panel** to track popular content
4. **Monitor file sizes** - Telegram has a 50MB limit
5. **Update yt-dlp regularly** - platforms change their APIs

---

## 🆘 Need Help?

1. Check `bot_app/README.md` for detailed docs
2. Review logs in admin panel: `/admin/bot_app/botlog/`
3. Use `python manage.py webhook_info` to debug
4. Check Django error log: `django_errors.log`

---

**Your bot is ready! Just set up the webhook after deploying to cPanel with HTTPS. 🎉**
