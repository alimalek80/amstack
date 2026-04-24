# cPanel Environment Variables Setup Guide

## For Production (cPanel)

Add these environment variables in your cPanel Python app configuration (as shown in the Environment variables section):

### Required Variables

| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | `8339817857:AAGjAOrbww0wgqFifxsc7jSH3c0ZWjNd8lk` |
| `TELEGRAM_WEBHOOK_URL` | `https://amstack.org/bot/webhook/YOUR_SECRET_TOKEN/` |
| `TELEGRAM_WEBHOOK_SECRET` | `(generate a random secret - see below)` |

### How to Add in cPanel

1. **Go to your Python app** in cPanel (Setup Python App)
2. **Scroll to "Environment variables" section**
3. **Click "Add variable"** for each variable above:
   - Enter the **Name** (e.g., `TELEGRAM_BOT_TOKEN`)
   - Enter the **Value** (the corresponding value from table)
   - Click **Add**

### Generate a Secret Token

Before adding `TELEGRAM_WEBHOOK_SECRET`, generate a random secret token:

**Option 1 - Using Terminal:**
```bash
openssl rand -hex 32
```

**Option 2 - Using Python:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 3 - Online Generator:**
Visit: https://www.random.org/strings/

Example secret: `xK9mN2pQ7rS4tU8vW1xY5zA3bC6dE0fG`

### Complete Webhook URL Example

After generating your secret, your webhook URL should look like:
```
https://amstack.org/bot/webhook/xK9mN2pQ7rS4tU8vW1xY5zA3bC6dE0fG/
```

⚠️ **Important:** 
- Keep the secret token secure
- Use the SAME secret in both `TELEGRAM_WEBHOOK_SECRET` and `TELEGRAM_WEBHOOK_URL`
- Don't share these values publicly

## After Adding Variables

1. **STOP and START** your Python app in cPanel (not just restart)
2. **Set the webhook:**
   ```bash
   python manage.py set_webhook
   ```
   
3. **Verify webhook:**
   ```bash
   python manage.py webhook_info
   ```

## Variables Already in cPanel

These are already set (from your screenshot):
- `DATABASE_ENGINE`
- `DATABASE_HOST`
- `DATABASE_NAME`
- `DATABASE_PASSWORD`
- `DATABASE_PORT`
- `DATABASE_USER`
- `DEFAULT_FROM_EMAIL`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_DEBUG`
- `DJANGO_SETTINGS_MODULE`
- `EMAIL_HOST`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST_USER`
- `EMAIL_PORT`
- `EMAIL_USE_SSL`
- `SITE_URL`

Just add the 3 Telegram variables to this list.

## Testing

After deploying:

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Send an Instagram/YouTube/Twitter link
5. Check admin panel: `https://amstack.org/admin/bot_app/`

## Troubleshooting

If webhook doesn't work:
```bash
python manage.py webhook_info
```

This will show any errors from Telegram.
