"""
Management command to run Telegram bot in polling mode (for local development)
Usage: python manage.py run_bot_polling
"""
import logging
import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from bot_app.models import TelegramUser, DownloadRequest
from bot_app.services import is_supported_url, download_media
from bot_app.views import (
    get_or_create_telegram_user,
    send_telegram_message,
    handle_start_command,
    handle_help_command,
    handle_media_url
)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run Telegram bot in polling mode (for local development only)'

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        
        if not token:
            self.stdout.write(self.style.ERROR('❌ TELEGRAM_BOT_TOKEN not configured'))
            self.stdout.write('Please set TELEGRAM_BOT_TOKEN in your .env file')
            return
        
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot in polling mode...'))
        self.stdout.write(self.style.WARNING('⚠️  This is for local development only'))
        self.stdout.write(self.style.WARNING('⚠️  For production on cPanel, use webhooks instead'))
        self.stdout.write('')
        
        # Create application
        app = ApplicationBuilder().token(token).build()
        
        # Add handlers
        app.add_handler(CommandHandler('start', self.start_handler))
        app.add_handler(CommandHandler('help', self.help_handler))
        app.add_handler(MessageHandler(filters.TEXT | filters.CAPTION, self.message_handler))
        
        self.stdout.write(self.style.SUCCESS('✓ Bot is running! Press Ctrl+C to stop'))
        self.stdout.write('')
        
        try:
            # Run polling
            app.run_polling(allowed_updates=['message'])
        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Bot stopped'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            raise
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_data = update.message.from_user
        chat_id = update.message.chat.id
        
        # Get or create user (wrap sync function in async)
        user = await sync_to_async(get_or_create_telegram_user)(user_data.to_dict())
        
        # Send welcome message
        start_text = (
            "<b>🎬 Alex Media Downloader</b>\n"
            "\n"
            "Send me a link and I'll download it for you.\n"
            "\n"
            "Supported formats:\n"
            "• Instagram Posts, Reels & Videos (instagram.com/reel/... or instagram.com/p/...)\n"
            "• YouTube Shorts (youtube.com/shorts/...)\n"
            "• X/Twitter (x.com/... or twitter.com/...)\n"
            "\n"
            "📸🎥 <i>Supports both images and videos!</i>"
        )
        await update.message.reply_text(start_text, parse_mode='HTML')
        
        LOG.info(f"User {user.username or user.telegram_id} started bot")
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "Short help:\n"
            "- Paste a link from:\n"
            "  • Instagram Posts, Reels & Videos (instagram.com/reel/... or instagram.com/p/...)\n"
            "  • YouTube Shorts (youtube.com/shorts/...)\n"
            "  • X/Twitter (x.com/... or twitter.com/...)\n"
            "- I'll download and send back the content (if under 49MB).\n"
            "\n"
            "📸🎥 Supports both images and videos!"
        )
        await update.message.reply_text(help_text)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        import tempfile
        import os
        from datetime import datetime
        from django.utils import timezone
        
        text = update.message.text or update.message.caption or ''
        user_data = update.message.from_user
        chat_id = update.message.chat.id
        
        if not text:
            await update.message.reply_text(
                'Please send a message containing a URL (Instagram, YouTube Shorts, or X/Twitter).'
            )
            return
        
        # Get or create user (wrap sync function in async)
        user = await sync_to_async(get_or_create_telegram_user)(user_data.to_dict())
        
        # Extract URL
        url = text.split()[0]
        LOG.info(f"Received URL from {user.username or user.telegram_id}: {url}")
        
        # Check if supported
        is_supported, platform = is_supported_url(url)
        
        if not is_supported:
            await update.message.reply_text(
                'Please send a valid URL. Supported formats:\n'
                '• Instagram Posts, Reels & Videos (instagram.com/reel/... or instagram.com/p/...)\n'
                '• YouTube Shorts (youtube.com/shorts/...)\n'
                '• X/Twitter (x.com/... or twitter.com/...)\n'
                '\n'
                '📸🎥 Supports both images and videos!'
            )
            return
        
        # Create download request (wrap in sync_to_async)
        download_request = await sync_to_async(DownloadRequest.objects.create)(
            user=user,
            url=url,
            platform=platform or 'unknown',
            status='pending'
        )
        
        # Send initial status
        status_msg = await update.message.reply_text(
            '⬇️ Downloading... This may take a few seconds depending on the content size.'
        )
        
        tmpdir = None
        start_time = datetime.now()
        
        try:
            # Update status
            download_request.status = 'downloading'
            await sync_to_async(download_request.save)()
            
            await status_msg.edit_text('⬇️ Downloading content...')
            
            # Download media
            tmpdir = tempfile.mkdtemp(prefix='bot_media_')
            media_path, media_type = download_media(url, tmpdir)
            
            if not os.path.exists(media_path):
                raise Exception("Downloaded file not found")
            
            filesize = os.path.getsize(media_path)
            LOG.info(f"Downloaded {media_type} size: {filesize/1024/1024:.2f} MB")
            
            # Update download request
            download_request.media_type = media_type
            download_request.file_size = filesize
            await sync_to_async(download_request.save)()
            
            # Check file size
            if filesize > 45_000_000:  # 45MB
                await status_msg.edit_text(
                    f'❌ File too large ({filesize/1024/1024:.1f} MB). Telegram limit is 50MB.\n'
                    'Try a different video or contact the bot admin for assistance.'
                )
                download_request.status = 'failed'
                download_request.error_message = 'File too large'
                await sync_to_async(download_request.save)()
                return
            
            if filesize == 0:
                raise Exception("Downloaded file is empty")
            
            # Update status
            download_request.status = 'uploading'
            await sync_to_async(download_request.save)()
            
            await status_msg.edit_text(
                f'📤 Uploading {media_type} ({filesize/1024/1024:.1f} MB)...'
            )
            
            # Send media
            with open(media_path, 'rb') as f:
                if media_type == 'image':
                    await update.message.reply_photo(photo=f)
                else:
                    await update.message.reply_video(video=f)
            
            # Update success message
            await status_msg.edit_text('Here you go!')
            
            # Mark as completed
            download_request.status = 'completed'
            download_request.completed_at = timezone.now()
            download_request.download_duration = (datetime.now() - start_time).total_seconds()
            await sync_to_async(download_request.save)()
            
            LOG.info(f"Successfully processed {media_type} from {platform} for {user.username or user.telegram_id}")
            
        except Exception as e:
            LOG.exception('Failed to download or send media')
            error_msg = str(e)
            
            # Update download request
            download_request.status = 'failed'
            download_request.error_message = error_msg
            download_request.completed_at = timezone.now()
            await sync_to_async(download_request.save)()
            
            # Send error message
            if 'private' in error_msg.lower() or '403' in error_msg:
                message = '❌ This content is private or restricted and cannot be downloaded.'
            elif 'not available' in error_msg.lower():
                message = '❌ This content is not available or has been deleted.'
            else:
                message = f'❌ Failed to download: {error_msg[:100]}'
            
            try:
                await status_msg.edit_text(message)
            except Exception:
                await update.message.reply_text(message)
        
        finally:
            # Cleanup
            if tmpdir and os.path.exists(tmpdir):
                try:
                    import shutil
                    shutil.rmtree(tmpdir)
                except Exception as cleanup_error:
                    LOG.error(f"Failed to cleanup temp directory: {cleanup_error}")
