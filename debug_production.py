#!/usr/bin/env python3
"""
Production Debugging Script for AMStack Django Project
This script helps identify common production issues that cause 500 errors.

Usage:
1. Upload this script to your cPanel Django project root
2. Run via SSH: python debug_production.py
3. Or add it as a Django management command
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line
import logging

logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables and configuration."""
    print("=" * 50)
    print("ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Critical settings
    checks = [
        ('DEBUG', settings.DEBUG),
        ('SECRET_KEY', '***' if settings.SECRET_KEY else 'NOT SET'),
        ('ALLOWED_HOSTS', settings.ALLOWED_HOSTS),
        ('DATABASE ENGINE', settings.DATABASES['default']['ENGINE']),
        ('DATABASE NAME', settings.DATABASES['default']['NAME']),
        ('STATIC_ROOT', settings.STATIC_ROOT),
        ('MEDIA_ROOT', settings.MEDIA_ROOT),
        ('AUTH_USER_MODEL', settings.AUTH_USER_MODEL),
    ]
    
    for check_name, value in checks:
        print(f"{check_name:20}: {value}")
    
    # Check environment variables
    print("\nCRITICAL ENVIRONMENT VARIABLES:")
    env_vars = [
        'DJANGO_SECRET_KEY',
        'DJANGO_DEBUG',
        'DJANGO_ALLOWED_HOSTS',
        'DATABASE_ENGINE',
        'DATABASE_NAME',
        'DATABASE_USER',
        'DATABASE_PASSWORD',
        'DATABASE_HOST',
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"{var:25}: ***SET***")
            else:
                print(f"{var:25}: {value}")
        else:
            print(f"{var:25}: NOT SET")


def check_database():
    """Test database connectivity."""
    print("\n" + "=" * 50)
    print("DATABASE CHECK")
    print("=" * 50)
    
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Database connection: SUCCESS")
            
        # Check if tables exist
        from django.core.management.sql import sql_all
        from django.apps import apps
        
        print("📊 Checking key models...")
        
        # Check User model
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_count = User.objects.count()
            print(f"✅ Users table: {user_count} users found")
        except Exception as e:
            print(f"❌ Users table error: {e}")
        
        # Check Blog models
        try:
            from blog.models import Post, Category
            post_count = Post.objects.count()
            category_count = Category.objects.count()
            print(f"✅ Blog posts: {post_count} posts, {category_count} categories")
        except Exception as e:
            print(f"❌ Blog models error: {e}")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")


def check_file_permissions():
    """Check file and directory permissions."""
    print("\n" + "=" * 50)
    print("FILE PERMISSIONS CHECK")
    print("=" * 50)
    
    directories_to_check = [
        settings.STATIC_ROOT,
        settings.MEDIA_ROOT,
        PROJECT_ROOT / 'logs' if (PROJECT_ROOT / 'logs').exists() else None,
        PROJECT_ROOT,
    ]
    
    for directory in directories_to_check:
        if directory and Path(directory).exists():
            path = Path(directory)
            permissions = oct(path.stat().st_mode)[-3:]
            print(f"📁 {path}: {permissions}")
            
            # Check if writable
            if path.is_dir():
                test_file = path / 'test_write.tmp'
                try:
                    test_file.touch()
                    test_file.unlink()
                    print(f"   ✅ Writable")
                except Exception as e:
                    print(f"   ❌ Not writable: {e}")
        elif directory:
            print(f"📁 {directory}: DOES NOT EXIST")


def check_imports():
    """Check if all required packages can be imported."""
    print("\n" + "=" * 50)
    print("IMPORT CHECK")
    print("=" * 50)
    
    required_packages = [
        'django',
        'markdown',
        'bleach',
        'pygments',
        'PIL',  # Pillow for ImageField
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: OK")
        except ImportError as e:
            print(f"❌ {package}: MISSING - {e}")


def test_blog_creation():
    """Test blog post creation functionality."""
    print("\n" + "=" * 50)
    print("BLOG CREATION TEST")
    print("=" * 50)
    
    try:
        from blog.models import Post, Category
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Check if we have a user to test with
        if not User.objects.exists():
            print("❌ No users found - create a superuser first")
            return
            
        test_user = User.objects.first()
        print(f"📝 Testing with user: {test_user.email}")
        
        # Try to create a test post
        test_post = Post(
            title="Test Post - Debug",
            slug="test-post-debug",
            excerpt="This is a test post for debugging",
            content="# Test Content\n\nThis is test markdown content.",
            author=test_user,
            is_published=False,  # Don't publish the test post
            is_free=True,
        )
        
        # Validate the post without saving
        test_post.full_clean()
        print("✅ Blog post validation: SUCCESS")
        
        # Test category creation
        if Category.objects.exists():
            test_category = Category.objects.first()
            test_post.category = test_category
            test_post.full_clean()
            print(f"✅ Category assignment: SUCCESS ({test_category.name})")
        else:
            print("ℹ️  No categories found - posts can be created without categories")
        
    except Exception as e:
        print(f"❌ Blog creation test failed: {e}")
        import traceback
        traceback.print_exc()


def check_logs():
    """Check if log files exist and are writable."""
    print("\n" + "=" * 50)
    print("LOGGING CHECK")
    print("=" * 50)
    
    log_files = [
        PROJECT_ROOT / 'django_errors.log',
        PROJECT_ROOT / 'blog_errors.log',
    ]
    
    for log_file in log_files:
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"📄 {log_file.name}: {size} bytes")
            
            # Show last few lines
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   Last entries:")
                        for line in lines[-3:]:
                            print(f"   {line.strip()}")
            except Exception as e:
                print(f"   ❌ Cannot read log: {e}")
        else:
            # Test if we can create the log file
            try:
                log_file.touch()
                print(f"✅ {log_file.name}: Can be created")
            except Exception as e:
                print(f"❌ {log_file.name}: Cannot create - {e}")


def main():
    """Run all diagnostic checks."""
    print("🔍 AMStack Production Debugging Tool")
    print(f"📍 Project path: {PROJECT_ROOT}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🎯 Django version: {django.VERSION}")
    
    check_environment()
    check_database()
    check_file_permissions()
    check_imports()
    check_logs()
    test_blog_creation()
    
    print("\n" + "=" * 50)
    print("DEBUGGING COMPLETE")
    print("=" * 50)
    print("\n📝 Next steps if you're still getting 500 errors:")
    print("1. Check the django_errors.log and blog_errors.log files")
    print("2. Set DJANGO_DEBUG=True temporarily to see detailed errors")
    print("3. Check cPanel error logs")
    print("4. Verify all environment variables are set in production")
    print("5. Check file permissions on media and static directories")
    

if __name__ == '__main__':
    main()