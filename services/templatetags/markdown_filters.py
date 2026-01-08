from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()


@register.filter
def markdown(value):
    """
    Render markdown text to HTML.
    Supports bold, italic, links, lists, headings, etc.
    """
    if not value:
        return value
    
    # Convert markdown to HTML with extra extensions
    html = md.markdown(value, extensions=['extra', 'nl2br'])
    
    # Mark as safe so Django renders the HTML
    return mark_safe(html)
