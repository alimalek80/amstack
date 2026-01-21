"""
Django Migration to Fix UTF-8 Charset Issues
Migration file: blog/migrations/0005_fix_utf8_charset.py

This migration fixes MySQL charset issues for UTF-8 content support.
"""

from django.db import migrations


class Migration(migrations.Migration):
    """
    Fix MySQL charset to support UTF-8 characters including emojis.
    
    This migration converts the blog_post table and its text columns
    to use utf8mb4 character set which properly supports all UTF-8 
    characters including emojis and special symbols.
    """
    
    atomic = False  # Allow this migration to run in non-atomic mode
    
    dependencies = [
        ('blog', '0004_post_price'),  # Update this to match your latest blog migration
    ]
    
    operations = [
        # Fix blog_post table charset
        migrations.RunSQL([
            # Convert entire table to utf8mb4
            "ALTER TABLE blog_post CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            
            # Ensure individual columns use utf8mb4
            "ALTER TABLE blog_post MODIFY title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY excerpt TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_post MODIFY slug VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            
            # Fix other blog tables
            "ALTER TABLE blog_category CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_category MODIFY name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_category MODIFY slug VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            
            "ALTER TABLE blog_tag CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_tag MODIFY name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "ALTER TABLE blog_tag MODIFY slug VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            
        ], reverse_sql=[
            # Reverse operations (convert back to latin1 if needed)
            "ALTER TABLE blog_post CONVERT TO CHARACTER SET latin1 COLLATE latin1_swedish_ci;",
            "ALTER TABLE blog_category CONVERT TO CHARACTER SET latin1 COLLATE latin1_swedish_ci;",
            "ALTER TABLE blog_tag CONVERT TO CHARACTER SET latin1 COLLATE latin1_swedish_ci;",
        ]),
    ]