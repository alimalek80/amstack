"""
Webhook views for Telegram Bot
"""
import os
import json
import logging
import tempfile
import asyncio
from datetime import datetime, date
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import requests

from .models import TelegramUser, DownloadRequest, BotStatistics, BotLog
from .services import is_supported_url, download_media

LOG = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'


def log_bot_event(level: str, message: str, user=None, url=None, exception=None, metadata=None):
    """Helper function to log bot events to database."""
    try:
        BotLog.objects.create(
            level=level,
            message=message,
            user=user,
            url=url,
            exception=str(exception) if exception else None,
            metadata=metadata
        )
    except Exception as e:
        LOG.error(f"Failed to log event: {e}")


def update_daily_statistics(platform=None, success=True, file_size=0):
    """Update daily statistics."""
    try:
        today = date.today()
        stats, created = BotStatistics.objects.get_or_create(date=today)
        
        stats.total_requests += 1
        if success:
            stats.successful_downloads += 1
            stats.total_data_transferred += file_size
            
            if platform == 'instagram':
                stats.instagram_downloads += 1
            elif platform == 'youtube':
                stats.youtube_downloads += 1
            elif platform == 'twitter':
                stats.twitter_downloads += 1
        else:
            stats.failed_downloads += 1
        
        stats.save()
    except Exception as e:
        LOG.error(f"Failed to update statistics: {e}")


def send_telegram_message(chat_id: int, text: str, parse_mode='HTML', reply_to_message_id=None):
    """Send a text message via Telegram API."""
    url = f'{TELEGRAM_API_URL}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
    }
    
    if reply_to_message_id:
        data['reply_to_message_id'] = reply_to_message_id
    
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        LOG.error(f"Failed to send message: {e}")
        raise


def edit_telegram_message(chat_id: int, message_id: int, text: str, parse_mode='HTML'):
    """Edit an existing message via Telegram API."""
    url = f'{TELEGRAM_API_URL}/editMessageText'
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': parse_mode,
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        LOG.error(f"Failed to edit message: {e}")
        raise


def send_telegram_video(chat_id: int, video_path: str, caption=None):
    """Send a video file via Telegram API."""
    url = f'{TELEGRAM_API_URL}/sendVideo'
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': chat_id}
            
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, data=data, files=files, timeout=120)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        LOG.error(f"Failed to send video: {e}")
        raise


def send_telegram_photo(chat_id: int, photo_path: str, caption=None):
    """Send a photo file via Telegram API."""
    url = f'{TELEGRAM_API_URL}/sendPhoto'
    
    try:
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            data = {'chat_id': chat_id}
            
            if caption:
                data['caption'] = caption
            
            response = requests.post(url, data=data, files=files, timeout=120)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        LOG.error(f"Failed to send photo: {e}")
        raise


def get_or_create_telegram_user(user_data: dict) -> TelegramUser:
    """Get or create a Telegram user from update data."""
    telegram_id = user_data['id']
    
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
        }
    )
    
    if not created:
        # Update user info
        user.username = user_data.get('username') or user.username
        user.first_name = user_data.get('first_name') or user.first_name
        user.last_name = user_data.get('last_name') or user.last_name
        user.last_interaction = timezone.now()
        user.save()
    
    return user


def handle_start_command(chat_id: int, user: TelegramUser):
    """Handle /start command."""
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
    send_telegram_message(chat_id, start_text)
    log_bot_event('info', 'User started bot', user=user)


def handle_help_command(chat_id: int, user: TelegramUser):
    """Handle /help command."""
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
    send_telegram_message(chat_id, help_text)
    log_bot_event('info', 'User requested help', user=user)


def handle_media_url(chat_id: int, user: TelegramUser, url: str):
    """Handle a media URL download request."""
    start_time = datetime.now()
    
    # Check if URL is supported
    is_supported, platform = is_supported_url(url)
    
    if not is_supported:
        send_telegram_message(
            chat_id,
            'Please send a valid URL. Supported formats:\n'
            '• Instagram Posts, Reels & Videos (instagram.com/reel/... or instagram.com/p/...)\n'
            '• YouTube Shorts (youtube.com/shorts/...)\n'
            '• X/Twitter (x.com/... or twitter.com/...)\n'
            '\n'
            '📸🎥 Supports both images and videos!'
        )
        return
    
    # Create download request
    download_request = DownloadRequest.objects.create(
        user=user,
        url=url,
        platform=platform or 'unknown',
        status='pending'
    )
    
    # Send initial status message
    try:
        response = send_telegram_message(
            chat_id,
            '⬇️ Downloading... This may take a few seconds depending on the content size.'
        )
        status_message_id = response['result']['message_id']
    except Exception as e:
        LOG.error(f"Failed to send initial message: {e}")
        return
    
    tmpdir = None
    try:
        # Update status
        download_request.status = 'downloading'
        download_request.save()
        
        edit_telegram_message(chat_id, status_message_id, '⬇️ Downloading content...')
        
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
        download_request.save()
        
        # Check file size
        if filesize > 45_000_000:  # 45MB
            edit_telegram_message(
                chat_id,
                status_message_id,
                f'❌ File too large ({filesize/1024/1024:.1f} MB). Telegram limit is 50MB.\n'
                'Try a different video or contact the bot admin for assistance.'
            )
            download_request.status = 'failed'
            download_request.error_message = 'File too large'
            download_request.save()
            update_daily_statistics(platform, success=False)
            return
        
        if filesize == 0:
            raise Exception("Downloaded file is empty")
        
        # Update status
        download_request.status = 'uploading'
        download_request.save()
        
        edit_telegram_message(
            chat_id,
            status_message_id,
            f'📤 Uploading {media_type} ({filesize/1024/1024:.1f} MB)...'
        )
        
        # Send media
        if media_type == 'image':
            send_telegram_photo(chat_id, media_path)
        else:
            send_telegram_video(chat_id, media_path)
        
        # Update success message
        edit_telegram_message(chat_id, status_message_id, 'Here you go!')
        
        # Mark as completed
        download_request.status = 'completed'
        download_request.completed_at = timezone.now()
        download_request.download_duration = (datetime.now() - start_time).total_seconds()
        download_request.save()
        
        # Update statistics
        update_daily_statistics(platform, success=True, file_size=filesize)
        
        log_bot_event(
            'info',
            f'Successfully downloaded {media_type} from {platform}',
            user=user,
            url=url,
            metadata={'file_size': filesize, 'duration': download_request.download_duration}
        )
        
    except Exception as e:
        LOG.exception('Failed to download or send media')
        error_msg = str(e)
        
        # Update download request
        download_request.status = 'failed'
        download_request.error_message = error_msg
        download_request.completed_at = timezone.now()
        download_request.save()
        
        # Send error message
        if 'private' in error_msg.lower() or '403' in error_msg:
            message = '❌ This content is private or restricted and cannot be downloaded.'
        elif 'not available' in error_msg.lower():
            message = '❌ This content is not available or has been deleted.'
        else:
            message = f'❌ Failed to download: {error_msg[:100]}'
        
        try:
            edit_telegram_message(chat_id, status_message_id, message)
        except Exception:
            send_telegram_message(chat_id, message)
        
        # Update statistics
        update_daily_statistics(platform, success=False)
        
        log_bot_event('error', f'Download failed: {error_msg}', user=user, url=url, exception=e)
        
    finally:
        # Cleanup
        if tmpdir and os.path.exists(tmpdir):
            try:
                import shutil
                shutil.rmtree(tmpdir)
            except Exception as cleanup_error:
                LOG.error(f"Failed to cleanup temp directory: {cleanup_error}")


@csrf_exempt
@require_POST
def telegram_webhook(request, token):
    """
    Main webhook endpoint for receiving Telegram updates.
    This is called by Telegram servers when users interact with the bot.
    
    Args:
        request: Django HTTP request
        token: Secret token from URL path for security validation
    """
    # Validate webhook secret token
    expected_token = getattr(settings, 'TELEGRAM_WEBHOOK_SECRET', '')
    if not expected_token or token != expected_token:
        LOG.warning(f"Invalid webhook token received: {token}")
        return HttpResponse('Forbidden', status=403)
    
    try:
        # Parse update data
        update_data = json.loads(request.body.decode('utf-8'))
        LOG.info(f"Received update: {json.dumps(update_data, indent=2)}")
        
        # Extract message data
        message = update_data.get('message')
        if not message:
            return JsonResponse({'ok': True})
        
        # Get user and chat info
        user_data = message.get('from')
        chat_id = message.get('chat', {}).get('id')
        
        if not user_data or not chat_id:
            return JsonResponse({'ok': True})
        
        # Get or create user
        user = get_or_create_telegram_user(user_data)
        
        # Check if user is blocked
        if user.is_blocked:
            send_telegram_message(chat_id, '❌ You are blocked from using this bot.')
            return JsonResponse({'ok': True})
        
        # Handle commands
        text = message.get('text', '') or message.get('caption', '')
        
        if text.startswith('/start'):
            handle_start_command(chat_id, user)
        elif text.startswith('/help'):
            handle_help_command(chat_id, user)
        elif text:
            # Extract URL from message
            url = text.split()[0] if text else None
            if url:
                handle_media_url(chat_id, user, url)
            else:
                send_telegram_message(
                    chat_id,
                    'Please send a message containing a URL (Instagram, YouTube Shorts, or X/Twitter).'
                )
        
        return JsonResponse({'ok': True})
        
    except Exception as e:
        LOG.exception('Error processing webhook')
        log_bot_event('critical', f'Webhook processing error: {str(e)}', exception=e)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


def webhook_info(request):
    """Display webhook information (for debugging)."""
    if not TELEGRAM_TOKEN:
        return JsonResponse({'error': 'TELEGRAM_BOT_TOKEN not configured'}, status=500)
    
    try:
        response = requests.get(f'{TELEGRAM_API_URL}/getWebhookInfo', timeout=10)
        webhook_info = response.json()
        return JsonResponse(webhook_info, json_dumps_params={'indent': 2})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
