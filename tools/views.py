from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from markdownx.utils import markdownify
import json

def markdown_live_preview(request):
    """Markdown live preview editor."""
    return render(request, 'tools/markdown_live_preview.html')

@csrf_exempt
def markdown_preview_api(request):
    """API endpoint for rendering markdown to HTML."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            markdown_text = data.get('markdown', '')
            
            # Use markdownx's markdownify function which uses the same settings from Django settings
            html = markdownify(markdown_text)
            return JsonResponse({'html': html})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
