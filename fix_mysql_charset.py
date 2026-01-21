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

def check_current_charset():
    """Check current charset settings in database."""
    print("\n" + "=" * 50)
    print("CURRENT CHARSET CHECK")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # Check database charset
        cursor.execute("SELECT DEFAULT_CHARACTER_SET_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s", [connection.settings_dict['NAME']])
        db_charset = cursor.fetchone()
        print(f"Database charset: {db_charset[0] if db_charset else 'Unknown'}")
        
        # Check table charsets
        tables_to_check = [
            'blog_post', 'blog_category', 'blog_tag', 
            'accounts_user', 'accounts_profile'
        ]
        
        for table in tables_to_check:
            try:
                cursor.execute("""
                    SELECT CCSA.character_set_name 
                    FROM information_schema.`TABLES` T,
                         information_schema.`COLLATION_CHARACTER_SET_APPLICABILITY` CCSA
                    WHERE CCSA.collation_name = T.table_collation
                      AND T.table_schema = %s
                      AND T.table_name = %s
                """, [connection.settings_dict['NAME'], table])
                result = cursor.fetchone()
                charset = result[0] if result else 'Not found'
                print(f"Table {table}: {charset}")
            except Exception as e:
                print(f"Table {table}: Error checking - {e}")

def fix_database_charset():
    """Fix database charset issues with multiple approaches."""
    print("=" * 50)
    print("MYSQL CHARSET FIX - ENHANCED")
    print("=" * 50)
    
    # Check current charset first
    check_current_charset()
    
    # Get database connection info
    db_settings = connection.settings_dict
    db_name = db_settings['NAME']
    
    print(f"\nDatabase: {db_name}")
    print(f"Engine: {db_settings['ENGINE']}")
    
    print("\n🔧 METHOD 1: Complete Database Fix (RECOMMENDED)")
    print("=" * 50)
    
    # More comprehensive SQL commands
    sql_commands_method1 = [
        # First, set the database charset
        f"ALTER DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix blog_post table completely
        f"DROP TABLE IF EXISTS `{db_name}`.`blog_post_backup`;",
        f"CREATE TABLE `{db_name}`.`blog_post_backup` AS SELECT * FROM `{db_name}`.`blog_post`;",
        f"ALTER TABLE `{db_name}`.`blog_post` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`blog_post` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix specific columns
        f"ALTER TABLE `{db_name}`.`blog_post` MODIFY `title` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`blog_post` MODIFY `content` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`blog_post` MODIFY `excerpt` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`blog_post` MODIFY `slug` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        
        # Fix Django admin log table (CRITICAL for admin panel)
        f"ALTER TABLE `{db_name}`.`django_admin_log` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`django_admin_log` MODIFY `object_repr` VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"ALTER TABLE `{db_name}`.`django_admin_log` MODIFY `change_message` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    ]
    
    print("Copy these commands to phpMyAdmin:")
    for cmd in sql_commands_method1:
        print(cmd)
    
    print("\n🔧 METHOD 2: Django Management Command (Alternative)")
    print("=" * 50)
    print("If Method 1 doesn't work, create a Django migration:")
    
    migration_code = '''
from django.db import migrations

class Migration(migrations.Migration):
    atomic = False
    
    dependencies = [
        ('blog', '0004_post_price'),  # Update this to your latest migration
    ]
    
    operations = [
        migrations.RunSQL([
            "ALTER TABLE blog_post CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY excerpt TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        ], reverse_sql=[
            "ALTER TABLE blog_post CONVERT TO CHARACTER SET latin1;",
        ]),
    ]
'''
    
    print("1. Create file: blog/migrations/0005_fix_utf8_charset.py")
    print("2. Add this content:")
    print(migration_code)
    print("3. Run: python manage.py migrate")
    
    print("\n🔧 METHOD 3: Recreate Tables (Nuclear Option)")
    print("=" * 50)
    print("If nothing else works:")
    print("1. Export your data: python manage.py dumpdata blog > blog_backup.json")
    print("2. Drop and recreate tables: python manage.py migrate blog zero")
    print("3. Recreate with proper charset: python manage.py migrate")
    print("4. Restore data: python manage.py loaddata blog_backup.json")

def advanced_charset_test():
    """More detailed charset testing."""
    print("\n" + "=" * 50)
    print("ADVANCED CHARSET TESTING")
    print("=" * 50)
    
    # Test different types of UTF-8 content
    test_cases = [
        ("Basic UTF-8", "Hello World! àáâãäå"),
        ("Emojis", "Test with emojis: 🚀 🎯 📝"),
        ("Chinese", "测试中文字符"),
        ("Arabic", "اختبار النص العربي"),
        ("Special symbols", "✓ ✗ → ← ↑ ↓ ☀ ☁ ☂"),
    ]
    
    from blog.models import Post
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    user = User.objects.first()
    
    if not user:
        print("❌ No users found")
        return
    
    failed_tests = []
    
    for test_name, test_content in test_cases:
        try:
            test_post = Post(
                title=f"Test: {test_name}",
                slug=f"test-{test_name.lower().replace(' ', '-')}",
                content=test_content,
                excerpt=test_content[:50],
                author=user,
                is_published=False
            )
            test_post.full_clean()  # Validate without saving
            test_post.save()  # Try to save
            test_post.delete()  # Clean up
            print(f"✅ {test_name}: SUCCESS")
        except Exception as e:
            failed_tests.append((test_name, str(e)))
            print(f"❌ {test_name}: {str(e)[:100]}...")
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} tests failed - charset fix needed")
        return False
    else:
        print(f"\n✅ All tests passed - charset is working!")
        return True

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
    print("🔧 AMStack MySQL Charset Fix Tool - ENHANCED")
    print("This will help fix your UTF-8 encoding issues.")
    
    fix_database_charset()
    create_media_directories()
    
    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("=" * 50)
    print("1. Try METHOD 1 first (copy SQL commands to phpMyAdmin)")
    print("2. If that doesn't work, use METHOD 2 (Django migration)")
    print("3. METHOD 3 is the nuclear option (recreate tables)")
    
    # Ask if user wants to test charset status
    response = input("\nDo you want to check current charset status? (y/n): ").lower().strip()
    if response.startswith('y'):
        check_current_charset()
    
    # Ask if user wants to test UTF-8 (after they've run fixes)
    response = input("\nHave you run the charset fix commands? Test UTF-8 now? (y/n): ").lower().strip()
    if response.startswith('y'):
        if advanced_charset_test():
            print("\n🎉 SUCCESS! Your database now supports UTF-8 properly!")
            print("You can now create blog posts with emojis and special characters!")
        else:
            print("\n❌ Charset issues still exist. Try the alternative methods above.")
    else:
        print("\n👆 Run the charset fix commands first, then test again!")

if __name__ == '__main__':
    main()