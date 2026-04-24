"""
Media download service for Telegram Bot
Contains all the logic for downloading media from Instagram, YouTube, and Twitter/X
"""
import os
import re
import logging
import tempfile
import requests
from typing import Optional, Tuple
from urllib.parse import unquote
from yt_dlp import YoutubeDL

LOG = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 45_000_000  # 45 MB to leave some margin under Telegram's limit


def is_supported_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Check if URL is supported and return (is_supported, platform).
    
    Returns:
        Tuple of (bool, platform_name or None)
    """
    if not url:
        return False, None
    
    url = url.strip().lower()
    
    # Check each platform
    if 'instagram.com' in url and ('/reel/' in url or '/tv/' in url or '/p/' in url):
        LOG.info(f"Detected Instagram URL: {url}")
        return True, 'instagram'
    elif 'youtube.com/shorts/' in url or 'youtu.be/' in url:
        LOG.info(f"Detected YouTube URL: {url}")
        return True, 'youtube'
    elif 'twitter.com' in url or 'x.com' in url:
        LOG.info(f"Detected Twitter/X URL: {url}")
        return True, 'twitter'
    
    return False, None


def get_instagram_image_url(url: str) -> Optional[str]:
    """
    Best-effort extraction of the primary image URL from a public Instagram post.
    Uses multiple strategies to find the image URL.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    clean_url = url.split('?')[0]
    if not clean_url.endswith('/'):
        clean_url += '/'

    # Strategy A: legacy media endpoint
    try:
        media_resp = requests.get(
            f"{clean_url}media/?size=l",
            headers=headers,
            timeout=10,
            allow_redirects=True
        )
        if media_resp.ok and media_resp.headers.get('content-type', '').startswith('image/'):
            LOG.info('Found image via media/?size=l')
            return media_resp.url
        if media_resp.history and media_resp.url and 'instagram' in media_resp.url:
            LOG.info('Found image via media/?size=l redirect')
            return media_resp.url
    except Exception as e:
        LOG.debug(f"media/?size=l extraction failed: {e}")

    # Strategy B: oEmbed
    try:
        oembed_resp = requests.get(
            'https://www.instagram.com/oembed/',
            params={'url': clean_url, 'omitscript': 'true'},
            headers=headers,
            timeout=10,
        )
        if oembed_resp.ok:
            data = oembed_resp.json()
            thumb = data.get('thumbnail_url')
            if thumb:
                LOG.info('Found image via oEmbed')
                return thumb
    except Exception as e:
        LOG.debug(f"oEmbed extraction failed: {e}")

    # Strategy C: GraphQL/JSON endpoint
    try:
        gql_url = f"{clean_url}?__a=1&__d=dis"
        gql_resp = requests.get(gql_url, headers=headers, timeout=10)
        if gql_resp.ok:
            data = gql_resp.json()
            media = data.get('graphql', {}).get('shortcode_media', {})
            display_url = media.get('display_url')
            if display_url:
                LOG.info('Found image via GraphQL')
                return display_url
            # Carousel: pick first item
            sidecar = media.get('edge_sidecar_to_children', {}).get('edges', [])
            if sidecar:
                first_item = sidecar[0].get('node', {})
                display_url = first_item.get('display_url')
                if display_url:
                    LOG.info('Found image via GraphQL carousel')
                    return display_url
    except Exception as e:
        LOG.debug(f"GraphQL extraction failed: {e}")

    # Strategy D: Parse HTML
    try:
        resp = requests.get(clean_url, headers=headers, timeout=10)
        resp.raise_for_status()
        page_content = resp.text

        # JSON-LD structured data
        json_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
        for json_text in re.findall(json_pattern, page_content, re.DOTALL):
            try:
                import json
                ld = json.loads(json_text)
                if isinstance(ld, dict) and 'image' in ld:
                    LOG.info('Found image via JSON-LD')
                    return ld['image']
            except Exception:
                continue

        # Open Graph
        og_match = re.search(r'<meta property="og:image" content="([^"]+)"', page_content)
        if og_match:
            LOG.info('Found image via Open Graph')
            return og_match.group(1)

        # display_url patterns
        patterns = [
            r'"display_url":"([^"]+\.jpg[^"]*)"',
            r'"display_url":"([^"]+\.jpeg[^"]*)"',
            r'"display_url":"([^"]+\.png[^"]*)"',
            r'"display_url":"([^"]+\.webp[^"]*)"',
            r'display_url=([^&]+\.jpg[^&]*)',
            r'src="([^"]+\.jpg[^"]*)"[^>]*alt="[^"]*Instagram[^"]*"',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, page_content)
            if matches:
                LOG.info('Found image via HTML pattern')
                return unquote(matches[0].replace('\\u0026', '&'))

        # Any big img tag from CDN
        img_pattern = r'<img[^>]+src="([^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"[^>]*>'
        for img in re.findall(img_pattern, page_content, re.IGNORECASE):
            if any(skip in img.lower() for skip in ['profile', 'avatar', 'icon', 'logo']):
                continue
            if 'instagram' in img or 'fbcdn' in img:
                LOG.info('Found image via CDN pattern')
                return unquote(img.replace('\\u0026', '&'))

    except Exception as e:
        LOG.debug(f"HTML parse extraction failed: {e}")

    return None


def download_media(url: str, target_dir: str) -> Tuple[str, str]:
    """
    Download media (video/image) using yt-dlp with improved error handling.
    
    Returns:
        Tuple of (file_path, media_type)
    
    Raises:
        Exception: If download fails
    """
    
    # First, try to determine if this is an image or video post
    media_type = 'video'  # default
    
    try:
        info_opts = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'extract_flat': False,
        }
        
        with YoutubeDL(info_opts) as ydl:
            LOG.info(f"Extracting info for URL: {url}")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise Exception("Could not extract media info")
            
            # Check if this is a video or image post
            if 'entries' in info:
                first_entry = info['entries'][0] if info['entries'] else info
                if first_entry.get('vcodec') == 'none' or not first_entry.get('url'):
                    media_type = 'image'
            elif info.get('vcodec') == 'none' or not info.get('url'):
                media_type = 'image'
                
    except Exception as e:
        # If info extraction fails with "no video", it's likely an image post
        if "no video" in str(e).lower():
            media_type = 'image'
            LOG.info("Detected image post from error message")
        else:
            LOG.warning(f"Could not extract info: {e}. Assuming video.")
    
    # Handle image posts for Instagram
    if media_type == 'image' and 'instagram.com' in url.lower():
        try:
            LOG.info("Attempting Instagram image extraction")
            image_url = get_instagram_image_url(url)

            if not image_url:
                raise Exception("Could not extract Instagram image URL")

            LOG.info(f"Found image URL: {image_url}")

            # Download the image
            img_response = requests.get(
                image_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=30
            )
            img_response.raise_for_status()
            
            # Determine file extension
            content_type = img_response.headers.get('content-type', '').lower()
            if '.jpg' in image_url.lower() or '.jpeg' in image_url.lower() or 'jpeg' in content_type:
                ext = 'jpg'
            elif '.png' in image_url.lower() or 'png' in content_type:
                ext = 'png'
            elif '.webp' in image_url.lower() or 'webp' in content_type:
                ext = 'webp'
            else:
                ext = 'jpg'
            
            # Extract post ID from URL for filename
            post_id_match = re.search(r'/p/([^/\?]+)', url)
            post_id = post_id_match.group(1) if post_id_match else 'image'
            
            filename = os.path.join(target_dir, f"{post_id}.{ext}")
            
            # Save the image
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            
            file_size = len(img_response.content)
            LOG.info(f"Downloaded image to: {filename}, size: {file_size/1024:.1f} KB")
            return filename, 'image'
            
        except Exception as img_error:
            LOG.error(f"Manual image extraction failed: {img_error}")
            # Fallback to yt-dlp
            pass
    
    # Video extraction or fallback
    ydl_opts = {
        'format': f'(mp4[filesize<{MAX_FILE_SIZE}]/best[filesize<{MAX_FILE_SIZE}])[ext=mp4]/mp4/best[ext=mp4]/best',
        'outtmpl': os.path.join(target_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'extractor_retries': 3,
        'file_access_retries': 3,
        'writeinfojson': False,
        'writethumbnail': False,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            LOG.info(f"Downloading {media_type} from URL: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                raise Exception("Download failed - no info returned")
            
            # Handle potential carousels
            if media_type == 'image' and 'entries' in info and len(info['entries']) > 1:
                media_id = info['entries'][0].get('id', 'media')
                ext = info['entries'][0].get('ext', 'jpg')
            else:
                media_id = info.get('id', 'media')
                ext = info.get('ext', 'mp4')
            
            filename = os.path.join(target_dir, f"{media_id}.{ext}")
            
            LOG.info(f"Expected filename: {filename}")
            
            # Verify file exists
            if not os.path.exists(filename):
                # Try to find any file in the directory
                files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
                if files:
                    filename = os.path.join(target_dir, files[0])
                    LOG.info(f"Found alternative file: {filename}")
                else:
                    raise FileNotFoundError("Downloaded file not found")
            
            # Verify file is not empty
            if os.path.getsize(filename) == 0:
                raise Exception("Downloaded file is empty")
            
            return filename, media_type
                    
    except Exception as e:
        LOG.error(f"yt-dlp download failed: {e}")
        error_str = str(e).lower()
        
        # Provide specific error messages
        if "private" in error_str:
            raise Exception("This content is private and cannot be downloaded")
        elif "not available" in error_str or "unavailable" in error_str:
            raise Exception("This content is not available or has been deleted")
        elif "403" in error_str or "forbidden" in error_str:
            raise Exception("Access denied. The content may be restricted")
        elif "login required" in error_str or "authentication" in error_str:
            raise Exception("This content requires login and cannot be downloaded")
        else:
            raise Exception(f"Download failed: {str(e)}")
