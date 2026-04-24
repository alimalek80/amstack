"""
Management command to remove Telegram webhook
Usage: python manage.py remove_webhook
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests


class Command(BaseCommand):
    help = 'Remove Telegram webhook for the bot'

    def handle(self, *args, **options):
        # Get bot token
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            raise CommandError('TELEGRAM_BOT_TOKEN not configured in settings')
        
        self.stdout.write('Removing webhook...')
        
        # Remove webhook
        api_url = f'https://api.telegram.org/bot{token}/deleteWebhook'
        
        try:
            response = requests.post(api_url, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                self.stdout.write(self.style.SUCCESS('✓ Webhook removed successfully!'))
                self.stdout.write(f"Description: {result.get('description', 'N/A')}")
            else:
                raise CommandError(f"Failed to remove webhook: {result.get('description', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Network error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
