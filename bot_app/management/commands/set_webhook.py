"""
Management command to set up Telegram webhook
Usage: python manage.py set_webhook
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Set up Telegram webhook for the bot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='The webhook URL (if not provided, will use TELEGRAM_WEBHOOK_URL from settings)',
        )

    def handle(self, *args, **options):
        # Get bot token
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            raise CommandError('TELEGRAM_BOT_TOKEN not configured in settings')
        
        # Get webhook URL
        webhook_url = options.get('url') or getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        if not webhook_url:
            raise CommandError(
                'Webhook URL not provided. Use --url option or set TELEGRAM_WEBHOOK_URL in settings.\n'
                'Example: python manage.py set_webhook --url https://yourdomain.com/bot/webhook/YOUR_SECRET_TOKEN/'
            )
        
        # Validate webhook URL
        if not webhook_url.startswith('https://'):
            raise CommandError('Webhook URL must use HTTPS')
        
        self.stdout.write(f'Setting webhook to: {webhook_url}')
        
        # Set webhook
        api_url = f'https://api.telegram.org/bot{token}/setWebhook'
        
        try:
            response = requests.post(
                api_url,
                json={
                    'url': webhook_url,
                    'max_connections': 40,
                    'allowed_updates': ['message'],
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                self.stdout.write(self.style.SUCCESS('✓ Webhook set successfully!'))
                self.stdout.write(f"Description: {result.get('description', 'N/A')}")
                
                # Get webhook info
                info_response = requests.get(f'https://api.telegram.org/bot{token}/getWebhookInfo', timeout=10)
                if info_response.ok:
                    info = info_response.json().get('result', {})
                    self.stdout.write('\nWebhook Info:')
                    self.stdout.write(f"  URL: {info.get('url', 'N/A')}")
                    self.stdout.write(f"  Pending updates: {info.get('pending_update_count', 0)}")
                    if info.get('last_error_date'):
                        self.stdout.write(self.style.WARNING(f"  Last error: {info.get('last_error_message', 'N/A')}"))
            else:
                raise CommandError(f"Failed to set webhook: {result.get('description', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Network error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
