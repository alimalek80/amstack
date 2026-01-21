#!/usr/bin/env python3
"""
MySQL Charset Fix Script for AMStack
This script fixes the UTF-8 encoding issues in your MySQL database.

Run this script after fixing the database charset in cPanel.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amstack.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_database_charset():
    """Fix database charset issues."""
    print("=" * 50)
    print("MYSQL CHARSET FIX")
    print("=" * 50)
    
    # Get database connection info
    db_settings = connection.settings_dict
    db_name = db_settings['NAME']
    
    print(f"Database: {db_name}")
    print(f"Engine: {db_settings['ENGINE']}")
    
    # SQL commands to fix charset
    sql_commands = [
        f"ALTER DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix blog_post table
        "ALTER TABLE blog_post CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_post MODIFY title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_post MODIFY content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_post MODIFY excerpt TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_post MODIFY slug VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix category table
        "ALTER TABLE blog_category CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_category MODIFY name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_category MODIFY slug VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix tag table
        "ALTER TABLE blog_tag CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_tag MODIFY name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE blog_tag MODIFY slug VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix user table
        "ALTER TABLE accounts_user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE accounts_user MODIFY email VARCHAR(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE accounts_user MODIFY full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix profile table
        "ALTER TABLE accounts_profile CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "ALTER TABLE accounts_profile MODIFY bio TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    ]
    
    print("\n📝 SQL Commands to run in cPanel MySQL:")
    print("=" * 50)
    for cmd in sql_commands:
        print(cmd)
    
    print("\n" + "=" * 50)
    print("MANUAL STEPS FOR cPanel:")
    print("=" * 50)
    print("1. Go to cPanel → phpMyAdmin")
    print("2. Select your database: fammkoqw_amstack_db")
    print("3. Click 'SQL' tab")
    print("4. Copy and paste each command above, one by one")
    print("5. Click 'Go' for each command")
    print("\nOR copy all commands at once and run them together.")

def test_utf8_content():
    """Test if UTF-8 content can be saved."""
    print("\n" + "=" * 50)
    print("TESTING UTF-8 CONTENT")
    print("=" * 50)
    
    try:
        from blog.models import Post
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.first()
        
        if not user:
            print("❌ No users found")
            return
        
        # Test with UTF-8 content
        test_content = """
        # Test Post with UTF-8 ✅
        
        This is a test with emojis: 🚀 🎯 📝 ✨
        
        Special characters: àáâãäåæçèéêë
        
        Symbols: ✓ ✗ → ← ↑ ↓
        """
        
        # Try to create and save
        test_post = Post.objects.create(
            title="UTF-8 Test Post ✅",
            slug="utf8-test-post",
            content=test_content,
            excerpt="Test post with UTF-8 characters ✨",
            author=user,
            is_published=False
        )
        
        print("✅ UTF-8 test post created successfully!")
        print(f"Post ID: {test_post.id}")
        
        # Clean up test post
        test_post.delete()
        print("✅ Test post cleaned up")
        
    except Exception as e:
        print(f"❌ UTF-8 test failed: {e}")
        print("You need to run the MySQL charset fix commands first!")

def create_media_directories():
    """Create missing media directories."""
    print("\n" + "=" * 50)
    print("CREATING MEDIA DIRECTORIES")
    print("=" * 50)
    
    media_dirs = [
        'media',
        'media/blog',
        'media/avatars',
    ]
    
    for dir_path in media_dirs:
        full_path = Path(dir_path)
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path}")
        else:
            print(f"ℹ️  Already exists: {dir_path}")
    
    print("\n🔧 Setting permissions...")
    import stat
    for dir_path in media_dirs:
        full_path = Path(dir_path)
        if full_path.exists():
            full_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)  # 755
            print(f"✅ Set 755 permissions: {dir_path}")

def main():
    print("🔧 AMStack MySQL Charset Fix Tool")
    print("This will help fix your UTF-8 encoding issues.")
    
    fix_database_charset()
    create_media_directories()
    
    print("\n" + "=" * 50)
    print("AFTER RUNNING THE SQL COMMANDS:")
    print("=" * 50)
    print("1. Run this script again to test UTF-8 content")
    print("2. Try creating a blog post with emojis")
    print("3. The 500 error should be resolved!")
    
    # Ask if user wants to test UTF-8 (after they've run SQL commands)
    response = input("\nHave you run the SQL commands in phpMyAdmin? (y/n): ").lower().strip()
    if response.startswith('y'):
        test_utf8_content()
    else:
        print("\n👆 Run the SQL commands first, then run this script again!")

if __name__ == '__main__':
    main()