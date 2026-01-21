# Production Settings for cPanel Deployment
# Create this file as 'production_settings.py' and use it in production

from .settings import *
import os

# SECURITY WARNING: Override with production values
DEBUG = False
ALLOWED_HOSTS = [
    'your-domain.com',  # Replace with your actual domain
    'www.your-domain.com',  # Replace with your actual domain
    # Add your IP if needed
]

# Database - Configure for production (MySQL/PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # or 'django.db.backends.postgresql'
        'NAME': os.getenv('DATABASE_NAME', 'your_db_name'),
        'USER': os.getenv('DATABASE_USER', 'your_db_user'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'your_db_password'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}

# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static and Media Files for cPanel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public_html', 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public_html', 'media')

# Logging - Enhanced for production debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_debug.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'blog_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'blog_errors.log'),
            'maxBytes': 1024*1024*2,  # 2 MB
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['file_error'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file_debug', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'blog': {
            'handlers': ['blog_file', 'file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'orders': {
            'handlers': ['file_error'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Email Configuration for Production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.your-domain.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'noreply@your-domain.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Make sure logs directory exists
import pathlib
pathlib.Path(BASE_DIR / 'logs').mkdir(exist_ok=True)