from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from markdownx.utils import markdownify
import json
import markdown
import weasyprint

# ── Google Fonts catalogue ──────────────────────────────────────────────────
# key: display name shown in the UI
# value: (google-fonts-family-query, css-font-stack)
HEADER_FONTS = {
    'Default (Arial)':      (None,                                  "'Arial','Helvetica Neue',sans-serif"),
    'Inter':                ('Inter:wght@400;600;700',              "'Inter',sans-serif"),
    'Poppins':              ('Poppins:wght@400;600;700',            "'Poppins',sans-serif"),
    'Raleway':              ('Raleway:wght@400;600;700',            "'Raleway',sans-serif"),
    'Montserrat':           ('Montserrat:wght@400;600;700',         "'Montserrat',sans-serif"),
    'Playfair Display':     ('Playfair+Display:wght@400;600;700',   "'Playfair Display',serif"),
    'Merriweather':         ('Merriweather:wght@300;400;700',       "'Merriweather',serif"),
    'Lora':                 ('Lora:wght@400;600;700',               "'Lora',serif"),
    'Vazirmatn':            ('Vazirmatn:wght@400;700',              "'Vazirmatn',sans-serif"),
}

BODY_FONTS = {
    'Default (Georgia)':    (None,                                  "'Georgia','Times New Roman',serif"),
    'Inter':                ('Inter:wght@400;700',                  "'Inter',sans-serif"),
    'Open Sans':            ('Open+Sans:wght@400;700',              "'Open Sans',sans-serif"),
    'Lato':                 ('Lato:wght@300;400;700',               "'Lato',sans-serif"),
    'Roboto':               ('Roboto:wght@300;400;700',             "'Roboto',sans-serif"),
    'Nunito':               ('Nunito:wght@400;700',                 "'Nunito',sans-serif"),
    'Merriweather':         ('Merriweather:wght@300;400;700',       "'Merriweather',serif"),
    'Lora':                 ('Lora:wght@400;700',                   "'Lora',serif"),
    'Source Serif 4':       ('Source+Serif+4:wght@400;700',         "'Source Serif 4',serif"),
    'Vazirmatn':            ('Vazirmatn:wght@400;700',              "'Vazirmatn',sans-serif"),
}

MARGIN_PRESETS = {
    'narrow':  1.5,
    'normal':  2.2,
    'wide':    3.0,
    'xwide':   4.0,
}


def _html_to_pdf(html: str) -> bytes:
    """Render HTML string to PDF bytes.

    Tries weasyprint first. If the server's libpango is too old
    (AttributeError on pango_context_set_round_glyph_positions),
    falls back to the pure-Python xhtml2pdf library.
    """
    try:
        return weasyprint.HTML(string=html).write_pdf()
    except (AttributeError, OSError):
        pass  # weasyprint failed – try xhtml2pdf fallback

    try:
        import io
        from xhtml2pdf import pisa
    except ImportError:
        raise RuntimeError(
            'PDF generation requires either weasyprint (with libpango >= 1.44) '
            'or xhtml2pdf. Install xhtml2pdf with: '
            'pip install xhtml2pdf --no-deps && '
            'pip install arabic-reshaper html5lib pypdf python-bidi "reportlab<5" '
            'pyHanko pyhanko-certvalidator'
        )

    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf)
    return buf.getvalue()


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
            html = markdownify(markdown_text)
            return JsonResponse({'html': html})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


def md_to_pdf(request):
    """Markdown to PDF converter – upload a .md file and download a styled PDF."""
    error = None

    if request.method == 'POST':
        uploaded = request.FILES.get('md_file')
        if not uploaded:
            error = 'Please select a Markdown file.'
        elif not uploaded.name.lower().endswith('.md'):
            error = 'Only .md files are accepted.'
        else:
            try:
                raw = uploaded.read().decode('utf-8')
            except UnicodeDecodeError:
                error = 'Could not read the file. Make sure it is a UTF-8 encoded Markdown file.'
            else:
                # ── Customisation (authenticated users only) ──────────────
                header_font_name = 'Default (Arial)'
                body_font_name   = 'Default (Georgia)'
                margin_cm        = 2.2

                if request.user.is_authenticated:
                    hf = request.POST.get('header_font', 'Default (Arial)')
                    bf = request.POST.get('body_font',   'Default (Georgia)')
                    mg = request.POST.get('margin_preset', 'normal')

                    if hf in HEADER_FONTS:
                        header_font_name = hf
                    if bf in BODY_FONTS:
                        body_font_name = bf
                    margin_cm = MARGIN_PRESETS.get(mg, 2.2)

                header_gf_query, header_css = HEADER_FONTS[header_font_name]
                body_gf_query,   body_css   = BODY_FONTS[body_font_name]

                # Build Google Fonts <link> tags (weasyprint fetches these at render time)
                gf_links = ''
                for query in {header_gf_query, body_gf_query}:
                    if query:
                        gf_links += (
                            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2'
                            f'?family={query}&display=swap">\n'
                        )

                margin = f'{margin_cm}cm'

                # Convert Markdown → HTML
                md = markdown.Markdown(extensions=[
                    'extra', 'toc', 'codehilite', 'nl2br', 'sane_lists',
                ])
                body_html = md.convert(raw)

                # Title from first H1 or filename
                title = uploaded.name.replace('.md', '')
                for line in raw.splitlines():
                    stripped = line.strip()
                    if stripped.startswith('# '):
                        title = stripped[2:].strip()
                        break

                full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{gf_links}
<style>
  @page {{
    size: A4;
    margin: {margin};
    @bottom-center {{
      content: counter(page) " / " counter(pages);
      font-family: {body_css};
      font-size: 9pt;
      color: #888;
    }}
  }}

  body {{
    font-family: {body_css};
    font-size: 11pt;
    line-height: 1.75;
    color: #1a1a2e;
    margin: 0;
    padding: 0;
  }}

  h1, h2, h3, h4, h5, h6 {{
    font-family: {header_css};
    color: #16213e;
    page-break-after: avoid;
    margin-top: 1.6em;
    margin-bottom: 0.4em;
  }}
  h1 {{
    font-size: 22pt;
    border-bottom: 3px solid #4f46e5;
    padding-bottom: 6pt;
    margin-top: 0;
    color: #0f3460;
  }}
  h2 {{
    font-size: 16pt;
    border-bottom: 1px solid #c7d2fe;
    padding-bottom: 3pt;
    color: #1e1b4b;
  }}
  h3 {{ font-size: 13pt; color: #312e81; }}
  h4 {{ font-size: 11pt; color: #4338ca; }}

  p {{ margin: 0.6em 0 0.8em; }}
  a {{ color: #4f46e5; text-decoration: underline; }}
  strong {{ color: #111; }}
  em {{ color: #374151; }}

  blockquote {{
    border-left: 4px solid #818cf8;
    margin: 1.2em 0;
    padding: 0.6em 1.2em;
    background: #f5f3ff;
    color: #3730a3;
    border-radius: 0 6px 6px 0;
    font-style: italic;
  }}

  code {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 9.5pt;
    background: #f1f5f9;
    color: #be185d;
    padding: 1px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }}
  pre {{
    background: #0f172a;
    color: #e2e8f0;
    padding: 12pt 14pt;
    border-radius: 8px;
    overflow: hidden;
    font-size: 9pt;
    line-height: 1.5;
    page-break-inside: avoid;
    margin: 1em 0;
  }}
  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.2em 0;
    font-size: 10pt;
    page-break-inside: avoid;
  }}
  th {{
    background: #4f46e5;
    color: #fff;
    font-family: {header_css};
    padding: 7pt 10pt;
    text-align: left;
    font-size: 9.5pt;
  }}
  td {{
    padding: 6pt 10pt;
    border-bottom: 1px solid #e2e8f0;
  }}
  tr:nth-child(even) td {{ background: #f8fafc; }}

  ul, ol {{ margin: 0.5em 0 0.8em 1.6em; padding: 0; }}
  li {{ margin-bottom: 0.25em; }}
  li > ul, li > ol {{ margin-top: 0.2em; }}

  hr {{
    border: none;
    border-top: 2px solid #c7d2fe;
    margin: 2em 0;
  }}

  img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    display: block;
    margin: 1em auto;
  }}

  .toc {{
    background: #f5f3ff;
    border: 1px solid #c7d2fe;
    border-radius: 8px;
    padding: 14pt 18pt;
    margin-bottom: 2em;
  }}
  .toc ul {{ margin: 0.3em 0 0 1.2em; }}
  .toc a {{ color: #4338ca; text-decoration: none; }}

  .footnote {{
    font-size: 9pt;
    color: #6b7280;
    border-top: 1px solid #e2e8f0;
    margin-top: 2em;
    padding-top: 0.6em;
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

                filename = uploaded.name.replace('.md', '.pdf')
                try:
                    pdf_bytes = _html_to_pdf(full_html)
                except Exception as exc:
                    error = f'PDF generation failed: {exc}'
                else:
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response

    context = {'error': error}
    return render(request, 'tools/md_to_pdf.html', context)
