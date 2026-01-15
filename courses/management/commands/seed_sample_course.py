from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

from courses.models import Course, Lesson


class Command(BaseCommand):
    help = "Seed a sample 'Build a Telegram Bot with Django' course with five lessons."

    def handle(self, *args, **options):
        title = "Build a Telegram Bot with Django"
        course, created = Course.objects.get_or_create(
            slug=slugify(title),
            defaults={
                'title': title,
                'description': "End-to-end guide to building and deploying a Telegram bot using Django.",
                'is_published': True,
                'is_free': True,
                'price': 0,
            },
        )

        lessons_data = [
            (
                "Project Setup and Bot Token",
                """
                ## Overview
                - Create a Django project and app
                - Install `python-telegram-bot` and set up environment variables
                - Obtain and store your Telegram bot token securely

                ## Steps
                1. `pip install python-telegram-bot`
                2. Add `.env` with `TELEGRAM_BOT_TOKEN=<your-token>`
                3. Wire up settings to load the token
                """,
            ),
            (
                "Webhook Endpoint and URLConf",
                """
                ## Overview
                - Add a webhook endpoint to receive Telegram updates
                - Configure URLs and CSRF exemption for the webhook

                ## Steps
                1. Create a Django view that parses JSON updates
                2. Route `/telegram/webhook/` to the view
                3. Verify payload structure with sample updates
                """,
            ),
            (
                "Command Handling and Dispatch",
                """
                ## Overview
                - Implement `/start` and `/help` commands
                - Add a simple echo handler for text messages

                ## Steps
                1. Build a dispatcher function that routes by command
                2. Add helpers to send replies via Telegram API
                3. Write basic unit tests for the dispatcher
                """,
            ),
            (
                "Persistence and User State",
                """
                ## Overview
                - Store chat/user state in the database
                - Track simple preferences and last interaction

                ## Steps
                1. Create a `BotUser` model with chat_id and settings
                2. Middleware/helper to load user state per update
                3. Add a `/prefs` command to toggle a setting
                """,
            ),
            (
                "Deployment and Webhook Configuration",
                """
                ## Overview
                - Deploy to a host (e.g., Render/Heroku/Fly.io)
                - Configure HTTPS endpoint and set Telegram webhook

                ## Steps
                1. Add Gunicorn and basic Procfile/service config
                2. Use `curl` to set webhook: `https://api.telegram.org/bot<TOKEN>/setWebhook?url=<your-url>/telegram/webhook/`
                3. Monitor logs and validate delivery
                """,
            ),
        ]

        created_count = 0
        for idx, (lesson_title, content) in enumerate(lessons_data, start=1):
            lesson, lesson_created = Lesson.objects.get_or_create(
                course=course,
                slug=slugify(f"{course.slug}-{lesson_title}"),
                defaults={
                    'title': lesson_title,
                    'excerpt': content.split("\n", 1)[0][:140],
                    'content': content.strip(),
                    'is_published': True,
                    'is_free': True,
                    'order': idx,
                    'published_at': timezone.now(),
                },
            )
            if lesson_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded course '{course.title}' (created={created}) with {created_count} new lessons."
        ))
