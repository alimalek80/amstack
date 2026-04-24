"""
Management command to get Telegram webhook info
Usage: python manage.py webhook_info
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import requests
import json


class Command(BaseCommand):
    help = 'Get Telegram webhook information'

    def handle(self, *args, **options):
        # Get bot token
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not token:
            raise CommandError('TELEGRAM_BOT_TOKEN not configured in settings')
        
        self.stdout.write('Fetching webhook info...\n')
        
        # Get webhook info
        api_url = f'https://api.telegram.org/bot{token}/getWebhookInfo'
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                info = result.get('result', {})
                
                self.stdout.write(self.style.SUCCESS('Webhook Information:'))
                self.stdout.write(f"  URL: {info.get('url', 'Not set')}")
                self.stdout.write(f"  Has custom certificate: {info.get('has_custom_certificate', False)}")
                self.stdout.write(f"  Pending update count: {info.get('pending_update_count', 0)}")
                self.stdout.write(f"  Max connections: {info.get('max_connections', 'N/A')}")
                
                if info.get('allowed_updates'):
                    self.stdout.write(f"  Allowed updates: {', '.join(info.get('allowed_updates'))}")
                
                if info.get('last_error_date'):
                    self.stdout.write(self.style.WARNING(f"\n  Last error date: {info.get('last_error_date')}"))
                    self.stdout.write(self.style.WARNING(f"  Last error message: {info.get('last_error_message', 'N/A')}"))
                
                if info.get('last_synchronization_error_date'):
                    self.stdout.write(self.style.WARNING(f"\n  Last sync error: {info.get('last_synchronization_error_date')}"))
                
                # Also get bot info
                bot_info_response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
                if bot_info_response.ok:
                    bot_info = bot_info_response.json().get('result', {})
                    self.stdout.write(f"\nBot Information:")
                    self.stdout.write(f"  Username: @{bot_info.get('username', 'N/A')}")
                    self.stdout.write(f"  Name: {bot_info.get('first_name', 'N/A')}")
                    self.stdout.write(f"  ID: {bot_info.get('id', 'N/A')}")
                
            else:
                raise CommandError(f"Failed to get webhook info: {result.get('description', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Network error: {str(e)}')
        except Exception as e:
            raise CommandError(f'Error: {str(e)}')
