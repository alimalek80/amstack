# Running the Telegram Bot Locally

## Quick Start (Polling Mode)

For local development, run the bot in **polling mode**:

```bash
# 1. Make sure your virtual environment is activated
source .venv/bin/activate

# 2. Make sure TELEGRAM_BOT_TOKEN is set in .env
# (already configured in your .env file)

# 3. Run the bot in polling mode
python manage.py run_bot_polling
```

You should see:
```
Starting Telegram bot in polling mode...
⚠️  This is for local development only
⚠️  For production on cPanel, use webhooks instead

✓ Bot is running! Press Ctrl+C to stop
```

## Testing Your Bot

1. **Find your bot on Telegram** (search for the username you got from @BotFather)
2. **Send `/start`** to start the bot
3. **Send a URL** from Instagram, YouTube, or Twitter/X
4. **Wait for download** - the bot will download and send you the media

## Example URLs to Test

**Instagram:**
- `https://www.instagram.com/p/ABC123/`
- `https://www.instagram.com/reel/XYZ456/`

**YouTube Shorts:**
- `https://www.youtube.com/shorts/ABC123`

**Twitter/X:**
- `https://twitter.com/user/status/123456789`
- `https://x.com/user/status/123456789`

## Stop the Bot

Press `Ctrl+C` in the terminal where the bot is running.

## Troubleshooting

### Bot doesn't respond

1. **Check your token in .env:**
   ```bash
   cat .env | grep TELEGRAM_BOT_TOKEN
   ```
   Should show: `TELEGRAM_BOT_TOKEN=8339817857:AAGjAOrbww0wgqFifxsc7jSH3c0ZWjNd8lk`

2. **Check if bot is running:**
   Look for "✓ Bot is running!" message in terminal

3. **Check for errors:**
   Look at terminal output for any error messages

### Downloads fail

1. **Update yt-dlp:**
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **Check URL format:**
   Make sure you're sending a valid URL from supported platforms

3. **Check file size:**
   Files over 50MB cannot be sent via Telegram

## Two Modes Explained

### 📱 Polling Mode (Local Development)
- ✅ Works on your computer
- ✅ No need for public URL
- ✅ Easy to test and debug
- ❌ Can't be used on cPanel (shared hosting)
- **Use:** `python manage.py run_bot_polling`

### 🌐 Webhook Mode (Production - cPanel)
- ✅ Works on servers (cPanel)
- ✅ More efficient for production
- ✅ Required for shared hosting
- ❌ Needs HTTPS public URL
- ❌ Can't be used locally without ngrok
- **Use:** Set webhook with `python manage.py set_webhook`

## Current Setup

- **Local:** Use polling mode (this guide)
- **Production (cPanel):** Use webhook based on CPANEL_TELEGRAM_SETUP.md

## View Logs

To see what's happening, check:
```bash
# Django logs
tail -f django_errors.log

# Or run with verbose output
python manage.py run_bot_polling
```

## Admin Panel

While bot is running, you can monitor activity at:
```
http://localhost:8000/admin/bot_app/
```

Login with your Django superuser account to see:
- Users interacting with the bot
- Download requests
- Statistics
- Logs

---

**Your bot is ready to test locally! 🎉**

Just run:
```bash
python manage.py run_bot_polling
```
