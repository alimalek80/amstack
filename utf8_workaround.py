"""
Temporary UTF-8 Content Filter for Blog Posts
Use this until MySQL charset is fixed.

Add this to your blog/models.py temporarily:
"""

import re
import unicodedata

def clean_utf8_content(text):
    """
    Clean text content to avoid MySQL charset issues.
    This is a temporary solution until database charset is fixed.
    """
    if not text:
        return text
    
    # Remove or replace problematic UTF-8 characters
    replacements = {
        # Emojis
        '🚀': '[rocket]',
        '🎯': '[target]', 
        '📝': '[memo]',
        '✅': '[check]',
        '❌': '[x]',
        '⚠️': '[warning]',
        '🔥': '[fire]',
        '💡': '[idea]',
        '📊': '[chart]',
        '🔧': '[tool]',
        
        # Special quotes
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        
        # Dashes
        '—': '-',
        '–': '-',
        
        # Other common symbols
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '✓': '[check]',
        '✗': '[x]',
    }
    
    # Apply replacements
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    
    # Remove any remaining problematic characters
    # Keep only ASCII and basic Latin characters
    text = ''.join(char for char in text if ord(char) < 256 or char.isspace())
    
    return text

# Add this method to your Post model temporarily:
"""
def save(self, *args, **kwargs):
    # Clean content before saving (temporary fix)
    if self.content:
        self.content = clean_utf8_content(self.content)
    if self.title:
        self.title = clean_utf8_content(self.title)
    if self.excerpt:
        self.excerpt = clean_utf8_content(self.excerpt)
    
    super().save(*args, **kwargs)
"""