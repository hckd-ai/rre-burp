"""
Web Helper Utilities
===================

Utility functions for common web interactions, element detection, and page manipulation.
"""

import asyncio
import time
from typing import List, Optional, Tuple, Union
from playwright.async_api import Page, Locator, ElementHandle
import logging

logger = logging.getLogger(__name__)


async def analyze_har_for_video_content(har_path: str) -> dict:
    """
    Analyze a HAR file to extract video-related network traffic and URLs
    
    Args:
        har_path: Path to the HAR file
        
    Returns:
        Dictionary with video analysis results
    """
    try:
        import json
        
        with open(har_path, 'r') as f:
            har_data = json.load(f)
        
        video_analysis = {
            'video_requests': [],
            'streaming_urls': [],
            'manifest_urls': [],
            'video_segments': [],
            'ad_requests': [],
            'total_requests': 0,
            'video_related_count': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return video_analysis
        
        entries = har_data['log']['entries']
        video_analysis['total_requests'] = len(entries)
        
        # Video file extensions
        video_extensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
        # Streaming formats
        streaming_formats = ['.m3u8', '.mpd', '.ts', '.m4s', '.mp4', '.webm']
        # Manifest patterns
        manifest_patterns = ['manifest', 'playlist', 'index', 'master', 'live']
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            
            # Check if this is a video-related request
            is_video_related = False
            
            # Check for video file extensions
            if any(ext in url.lower() for ext in video_extensions):
                is_video_related = True
                video_analysis['video_requests'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'size': response.get('bodySize', 0),
                    'content_type': response.get('content', {}).get('mimeType', ''),
                    'type': 'video_file'
                })
            
            # Check for streaming manifests
            if any(ext in url.lower() for ext in ['.m3u8', '.mpd']):
                is_video_related = True
                video_analysis['manifest_urls'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'type': 'manifest'
                })
            
            # Check for video segments
            if any(ext in url.lower() for ext in ['.ts', '.m4s']):
                is_video_related = True
                video_analysis['video_segments'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'size': response.get('bodySize', 0),
                    'type': 'segment'
                })
            
            # Check for streaming URLs in manifest patterns
            if any(pattern in url.lower() for pattern in manifest_patterns):
                if any(ext in url.lower() for ext in streaming_formats):
                    is_video_related = True
                    video_analysis['streaming_urls'].append({
                        'url': url,
                        'method': request.get('method', ''),
                        'status': response.get('status', 0),
                        'type': 'streaming'
                    })
            
            # Check content type for video
            content_type = response.get('content', {}).get('mimeType', '')
            if content_type and ('video' in content_type or 'application/x-mpegURL' in content_type or 'application/dash+xml' in content_type):
                is_video_related = True
                if url not in [req['url'] for req in video_analysis['video_requests']]:
                    video_analysis['video_requests'].append({
                        'url': url,
                        'method': request.get('method', ''),
                        'status': response.get('status', 0),
                        'size': response.get('bodySize', 0),
                        'content_type': content_type,
                        'type': 'video_content'
                    })
            
            # Check for ad-related requests
            if any(ad_pattern in url.lower() for ad_pattern in ['ads', 'advertising', 'doubleclick', 'googlesyndication', 'adserver']):
                video_analysis['ad_requests'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'type': 'ad'
                })
            
            if is_video_related:
                video_analysis['video_related_count'] += 1
        
        return video_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing HAR file {har_path}: {e}")
        return {
            'error': str(e),
            'video_requests': [],
            'streaming_urls': [],
            'manifest_urls': [],
            'video_segments': [],
            'ad_requests': [],
            'total_requests': 0,
            'video_related_count': 0
        }


async def wait_for_page_stable(page: Page, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
    """
    Wait for the page to become stable (no network activity, DOM changes, etc.)
    
    Args:
        page: Playwright page object
        timeout: Maximum time to wait
        check_interval: How often to check for stability
        
    Returns:
        True if page is stable, False if timeout
    """
    start_time = time.time()
    last_height = 0
    last_network_idle = True
    
    while time.time() - start_time < timeout:
        try:
            # Check if page is still loading
            if page.url == "about:blank":
                await asyncio.sleep(check_interval)
                continue
                
            # Check for network idle
            try:
                network_idle = await page.evaluate("() => !navigator.onLine || document.readyState === 'complete'")
            except:
                network_idle = True
            
            # Check for DOM changes
            current_height = await page.evaluate("() => document.body.scrollHeight")
            
            # Check for ongoing requests
            ongoing_requests = len(page.request._ongoing_requests)
            
            # If everything is stable, return True
            if (network_idle and 
                current_height == last_height and 
                ongoing_requests == 0 and
                last_network_idle):
                return True
                
            last_height = current_height
            last_network_idle = network_idle
            
        except Exception as e:
            logger.debug(f"Error checking page stability: {e}")
            
        await asyncio.sleep(check_interval)
    
    return False


async def find_and_click_element(page: Page, selectors: List[str], 
                               text_patterns: Optional[List[str]] = None,
                               max_attempts: int = 3) -> bool:
    """
    Find and click an element using multiple selector strategies
    
    Args:
        page: Playwright page object
        selectors: List of CSS selectors to try
        text_patterns: Optional text patterns to match
        max_attempts: Maximum number of click attempts
        
    Returns:
        True if element was found and clicked, False otherwise
    """
    for attempt in range(max_attempts):
        try:
            # Try each selector
            for selector in selectors:
                try:
                    # Wait for element to be visible
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.wait_for(state="visible", timeout=2000)
                        
                        # Check if element is clickable
                        if await element.is_enabled():
                            await element.click()
                            logger.info(f"Successfully clicked element with selector: {selector}")
                            return True
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no selector worked, try text-based search
            if text_patterns:
                for text in text_patterns:
                    try:
                        # Try to find by text content
                        element = page.get_by_text(text, exact=False).first
                        if await element.count() > 0:
                            await element.wait_for(state="visible", timeout=2000)
                            if await element.is_enabled():
                                await element.click()
                                logger.info(f"Successfully clicked element with text: {text}")
                                return True
                    except Exception as e:
                        logger.debug(f"Text search for '{text}' failed: {e}")
                        continue
            
            # Wait a bit before retry
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.debug(f"Click attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(1)
    
    logger.warning(f"Failed to find and click element after {max_attempts} attempts")
    return False


async def handle_cookie_consent(page: Page, config) -> bool:
    """
    Handle cookie consent dialogs intelligently
    
    Args:
        page: Playwright page object
        config: CookieConsentConfig object
        
    Returns:
        True if consent was handled, False otherwise
    """
    try:
        logger.info("Looking for cookie consent dialogs...")
        
        # Wait a bit for dialogs to appear
        await asyncio.sleep(2)
        
        # Try to find and handle consent dialogs
        for selector in config.selectors:
            try:
                elements = page.locator(selector)
                if await elements.count() > 0:
                    logger.info(f"Found cookie consent dialog with selector: {selector}")
                    
                    # Try to find and click accept buttons
                    for button_text in config.button_texts:
                        try:
                            # Look for buttons with the text
                            button = page.get_by_role("button", name=button_text, exact=False).first
                            if await button.count() > 0:
                                await button.wait_for(state="visible", timeout=2000)
                                if await button.is_enabled():
                                    await button.click()
                                    logger.info(f"Clicked cookie consent button: {button_text}")
                                    await asyncio.sleep(config.wait_after_consent)
                                    return True
                        except Exception as e:
                            logger.debug(f"Button text '{button_text}' failed: {e}")
                            continue
                    
                    # If no button text worked, try common button selectors
                    button_selectors = [
                        'button[type="button"]',
                        'button[type="submit"]',
                        'input[type="button"]',
                        'input[type="submit"]',
                        'a[role="button"]'
                    ]
                    
                    for btn_selector in button_selectors:
                        try:
                            buttons = page.locator(f"{selector} {btn_selector}")
                            if await buttons.count() > 0:
                                # Click the first button
                                await buttons.first.click()
                                logger.info(f"Clicked cookie consent button with selector: {btn_selector}")
                                await asyncio.sleep(config.wait_after_consent)
                                return True
                        except Exception as e:
                            logger.debug(f"Button selector {btn_selector} failed: {e}")
                            continue
                            
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        logger.info("No cookie consent dialog found or handled")
        return False
        
    except Exception as e:
        logger.error(f"Error handling cookie consent: {e}")
        return False


async def handle_ads_and_overlays(page: Page, config) -> bool:
    """
    Handle advertisements and overlays intelligently
    
    Args:
        page: Playwright page object
        config: AdHandlingConfig object
        
    Returns:
        True if ads were handled, False otherwise
    """
    try:
        logger.info("Looking for ads and overlays...")
        
        # Wait a bit for ads to load
        await asyncio.sleep(3)
        
        ads_handled = False
        
        # Look for ad elements
        for selector in config.ad_selectors:
            try:
                elements = page.locator(selector)
                if await elements.count() > 0:
                    logger.info(f"Found ad/overlay with selector: {selector}")
                    
                    # Try to find skip buttons
                    for skip_selector in config.skip_selectors:
                        try:
                            skip_elements = page.locator(f"{selector} {skip_selector}")
                            if await skip_elements.count() > 0:
                                await skip_elements.first.click()
                                logger.info(f"Clicked skip button: {skip_selector}")
                                await asyncio.sleep(config.wait_after_skip)
                                ads_handled = True
                                break
                        except Exception as e:
                            logger.debug(f"Skip selector {skip_selector} failed: {e}")
                            continue
                    
                    # If no skip button, try to close the ad
                    if not ads_handled:
                        try:
                            # Look for close buttons
                            close_selectors = [
                                '[aria-label*="Close"]',
                                '[title*="Close"]',
                                '[class*="close"]',
                                '[id*="close"]',
                                'button:contains("×")',
                                'button:contains("Close")'
                            ]
                            
                            for close_selector in close_selectors:
                                try:
                                    close_elements = page.locator(f"{selector} {close_selector}")
                                    if await close_elements.count() > 0:
                                        await close_elements.first.click()
                                        logger.info(f"Closed ad with selector: {close_selector}")
                                        await asyncio.sleep(config.wait_after_skip)
                                        ads_handled = True
                                        break
                                except Exception as e:
                                    logger.debug(f"Close selector {close_selector} failed: {e}")
                                    continue
                                    
                        except Exception as e:
                            logger.debug(f"Error trying to close ad: {e}")
                            
            except Exception as e:
                logger.debug(f"Ad selector {selector} failed: {e}")
                continue
        
        # Wait for ads to finish if we couldn't handle them
        if not ads_handled:
            logger.info("Waiting for ads to finish...")
            await asyncio.sleep(min(10, config.max_ad_wait))
        
        return ads_handled
        
    except Exception as e:
        logger.error(f"Error handling ads and overlays: {e}")
        return False


async def scroll_page_intelligently(page: Page, config) -> None:
    """
    Scroll the page intelligently to load dynamic content
    
    Args:
        page: Playwright page object
        config: SiteExplorerConfig object
    """
    try:
        logger.info("Starting intelligent page scrolling...")
        
        for attempt in range(config.max_scroll_attempts):
            try:
                # Get current scroll position
                current_position = await page.evaluate("() => window.pageYOffset")
                
                # Scroll down
                await page.evaluate("() => window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(config.scroll_pause)
                
                # Check if we've reached the bottom
                new_position = await page.evaluate("() => window.pageYOffset")
                if new_position == current_position:
                    logger.info("Reached end of page")
                    break
                
                # Wait for content to load
                await wait_for_page_stable(page, timeout=5.0)
                
            except Exception as e:
                logger.debug(f"Scroll attempt {attempt + 1} failed: {e}")
                if attempt < config.max_scroll_attempts - 1:
                    await asyncio.sleep(1)
        
        # Scroll back to top
        await page.evaluate("() => window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        
        logger.info("Page scrolling completed")
        
    except Exception as e:
        logger.error(f"Error during page scrolling: {e}")


async def detect_video_content(page: Page, config) -> Optional[dict]:
    """
    Detect video content on the page with enhanced intelligence
    
    Args:
        page: Playwright page object
        config: VideoDetectionConfig object
        
    Returns:
        Dictionary with video information or None if no video found
    """
    try:
        logger.info("Looking for video content...")
        
        # Wait for page to be stable
        await wait_for_page_stable(page, timeout=config.video_load_wait)
        
        video_info = {
            'type': None,
            'selector': None,
            'duration': None,
            'src': None,
            'title': None,
            'player_type': None,
            'page_url': page.url,  # Store the current page URL where video was found
            'video_url': None,     # Store the actual video source URL
            'navigation_history': []  # Track navigation steps to find video
        }
        
        # First, try to detect immediate video content
        immediate_video = await _detect_immediate_video_content(page, config)
        if immediate_video:
            return immediate_video
        
        # If no immediate video, try to find video content areas and navigate to them
        logger.info("No immediate video found, searching for video content areas...")
        video_content_found = await _navigate_to_video_content(page, config)
        
        if video_content_found:
            # Wait for video content to load
            await asyncio.sleep(3)
            await wait_for_page_stable(page, timeout=config.video_load_wait)
            
            # Try to detect video again after navigation
            immediate_video = await _detect_immediate_video_content(page, config)
            if immediate_video:
                return immediate_video
        
        # Final attempt: look for video thumbnails and try to trigger them
        logger.info("Attempting to trigger video content from thumbnails...")
        video_triggered = await _trigger_video_from_thumbnails(page, config)
        
        if video_triggered:
            await asyncio.sleep(3)
            await wait_for_page_stable(page, timeout=config.video_load_wait)
            
            immediate_video = await _detect_immediate_video_content(page, config)
            if immediate_video:
                return immediate_video
        
        logger.info("No video content detected after all attempts")
        return None
        
    except Exception as e:
        logger.error(f"Error detecting video content: {e}")
        return None


async def _detect_immediate_video_content(page: Page, config) -> Optional[dict]:
    """
    Detect video content that's immediately visible on the page
    """
    video_info = {
        'type': None,
        'selector': None,
        'duration': None,
        'src': None,
        'title': None,
        'player_type': None,
        'page_url': page.url,  # Store the current page URL where video was found
        'video_url': None,     # Store the actual video source URL
        'navigation_history': [],  # Track navigation steps to find video
        'video_urls': [],      # Store all detected video URLs
        'stream_urls': [],     # Store streaming URLs
        'manifest_urls': []    # Store manifest/playlist URLs
    }
    
    # Check for native video elements
    for selector in config.video_selectors:
        try:
            elements = page.locator(selector)
            if await elements.count() > 0:
                logger.info(f"Found video element with selector: {selector}")
                
                # Get video information
                video_element = elements.first
                
                # Check if it's a native video element
                tag_name = await video_element.evaluate("el => el.tagName.toLowerCase()")
                
                if tag_name == 'video':
                    video_info['type'] = 'native'
                    video_info['selector'] = selector
                    
                    # Try to get duration
                    try:
                        duration = await video_element.evaluate("el => el.duration")
                        if duration and duration > config.min_video_duration:
                            video_info['duration'] = duration
                            
                            # Get all possible video sources
                            sources = await video_element.evaluate("""
                                el => {
                                    const sources = [];
                                    // Check src attribute
                                    if (el.src) sources.push(el.src);
                                    // Check source elements
                                    const sourceEls = el.querySelectorAll('source');
                                    sourceEls.forEach(source => {
                                        if (source.src) sources.push(source.src);
                                    });
                                    // Check data attributes
                                    if (el.dataset.src) sources.push(el.dataset.src);
                                    if (el.dataset.video) sources.push(el.dataset.video);
                                    return sources;
                                }
                            """)
                            
                            if sources:
                                video_info['video_urls'] = sources
                                video_info['src'] = sources[0]  # Primary source
                                video_info['video_url'] = sources[0]
                            
                            # Get title from various sources
                            title = await video_element.evaluate("""
                                el => {
                                    return el.title || el.alt || el.getAttribute('aria-label') || 
                                           el.getAttribute('data-title') || el.getAttribute('data-name') ||
                                           el.closest('[data-title]')?.getAttribute('data-title') ||
                                           el.closest('[data-name]')?.getAttribute('data-name') ||
                                           el.closest('.title')?.textContent ||
                                           el.closest('.name')?.textContent;
                                }
                            """)
                            video_info['title'] = title
                            
                            logger.info(f"Found native video: {title} (duration: {duration}s) at URL: {page.url}")
                            logger.info(f"Video sources: {sources}")
                            return video_info
                    except Exception as e:
                        logger.debug(f"Error getting video duration: {e}")
                
                elif tag_name == 'iframe':
                    video_info['type'] = 'embedded'
                    video_info['selector'] = selector
                    iframe_src = await video_element.get_attribute('src')
                    video_info['src'] = iframe_src
                    video_info['video_url'] = iframe_src
                    video_info['video_urls'] = [iframe_src] if iframe_src else []
                    
                    # Determine player type from src
                    if 'youtube' in iframe_src:
                        video_info['player_type'] = 'youtube'
                    elif 'vimeo' in iframe_src:
                        video_info['player_type'] = 'vimeo'
                    elif 'dailymotion' in iframe_src:
                        video_info['player_type'] = 'dailymotion'
                    elif 'twitch' in iframe_src:
                        video_info['player_type'] = 'twitch'
                    else:
                        video_info['player_type'] = 'custom'
                    
                    logger.info(f"Found embedded video: {video_info['player_type']} at URL: {page.url}")
                    logger.info(f"Video iframe URL: {iframe_src}")
                    return video_info
                    
        except Exception as e:
            logger.debug(f"Video selector {selector} failed: {e}")
            continue
    
    # Check for custom video players
    for selector in config.player_selectors:
        try:
            elements = page.locator(selector)
            if await elements.count() > 0:
                logger.info(f"Found video player with selector: {selector}")
                
                # Look for play buttons
                for play_selector in config.play_selectors:
                    try:
                        play_elements = page.locator(f"{selector} {play_selector}")
                        if await play_elements.count() > 0:
                            video_info['type'] = 'custom_player'
                            video_info['selector'] = selector
                            video_info['player_type'] = 'custom'
                            
                            # Try to get title from player
                            try:
                                title = await elements.first.evaluate("""
                                    el => {
                                        const titleEl = el.querySelector('[title], [aria-label], .title, .name, [data-title], [data-name]');
                                        return titleEl ? titleEl.textContent || titleEl.title || titleEl.getAttribute('aria-label') || 
                                               titleEl.getAttribute('data-title') || titleEl.getAttribute('data-name') : null;
                                    }
                                """)
                                video_info['title'] = title
                            except:
                                pass
                            
                            # Look for video URLs in the player
                            try:
                                video_urls = await elements.first.evaluate("""
                                    el => {
                                        const urls = [];
                                        // Check for video sources
                                        const sources = el.querySelectorAll('source, [data-src], [data-video], [data-stream]');
                                        sources.forEach(source => {
                                            if (source.src) urls.push(source.src);
                                            if (source.dataset.src) urls.push(source.dataset.src);
                                            if (source.dataset.video) urls.push(source.dataset.video);
                                            if (source.dataset.stream) urls.push(source.dataset.stream);
                                        });
                                        // Check for manifest/playlist URLs
                                        const manifests = el.querySelectorAll('[data-manifest], [data-playlist], [data-m3u8], [data-mpd]');
                                        manifests.forEach(manifest => {
                                            if (manifest.dataset.manifest) urls.push(manifest.dataset.manifest);
                                            if (manifest.dataset.playlist) urls.push(manifest.dataset.playlist);
                                            if (manifest.dataset.m3u8) urls.push(manifest.dataset.m3u8);
                                            if (manifest.dataset.mpd) urls.push(manifest.dataset.mpd);
                                        });
                                        return urls;
                                    }
                                """)
                                if video_urls:
                                    video_info['video_urls'] = video_urls
                                    video_info['video_url'] = video_urls[0]
                            except:
                                pass
                            
                            logger.info(f"Found custom video player: {title or 'Unknown'} at URL: {page.url}")
                            if video_info.get('video_urls'):
                                logger.info(f"Video URLs found: {video_info['video_urls']}")
                            return video_info
                            
                    except Exception as e:
                        logger.debug(f"Play selector {play_selector} failed: {e}")
                        continue
                        
        except Exception as e:
            logger.debug(f"Player selector {selector} failed: {e}")
            continue
    
    # Check for HLS/DASH manifests and streaming URLs
    try:
        streaming_urls = await page.evaluate("""
            () => {
                const urls = [];
                // Look for HLS manifests
                const hlsElements = document.querySelectorAll('[data-hls], [data-m3u8], [data-playlist]');
                hlsElements.forEach(el => {
                    if (el.dataset.hls) urls.push({type: 'hls', url: el.dataset.hls});
                    if (el.dataset.m3u8) urls.push({type: 'hls', url: el.dataset.m3u8});
                    if (el.dataset.playlist) urls.push({type: 'hls', url: el.dataset.playlist});
                });
                // Look for DASH manifests
                const dashElements = document.querySelectorAll('[data-dash], [data-mpd]');
                dashElements.forEach(el => {
                    if (el.dataset.dash) urls.push({type: 'dash', url: el.dataset.dash});
                    if (el.dataset.mpd) urls.push({type: 'dash', url: el.dataset.mpd});
                });
                // Look for video URLs in scripts
                const scripts = document.querySelectorAll('script');
                scripts.forEach(script => {
                    if (script.textContent) {
                        const hlsMatch = script.textContent.match(/["']([^"']*\\.m3u8[^"']*)["']/g);
                        const dashMatch = script.textContent.match(/["']([^"']*\\.mpd[^"']*)["']/g);
                        if (hlsMatch) hlsMatch.forEach(match => urls.push({type: 'hls', url: match.slice(1, -1)}));
                        if (dashMatch) dashMatch.forEach(match => urls.push({type: 'dash', url: match.slice(1, -1)}));
                    }
                });
                return urls;
            }
        """)
        
        if streaming_urls:
            video_info['type'] = 'streaming'
            video_info['stream_urls'] = streaming_urls
            video_info['video_urls'] = [url['url'] for url in streaming_urls]
            video_info['video_url'] = streaming_urls[0]['url'] if streaming_urls else None
            
            logger.info(f"Found streaming URLs: {streaming_urls}")
            return video_info
            
    except Exception as e:
        logger.debug(f"Error checking for streaming URLs: {e}")
    
    return None


async def _navigate_to_video_content(page: Page, config) -> bool:
    """
    Navigate to video content areas when videos aren't immediately visible
    """
    try:
        logger.info("Searching for video content areas...")
        
        # Common video content navigation patterns
        video_navigation_patterns = [
            # Navigation menus
            {'selector': '[href*="watch"]', 'text': None, 'description': 'Watch section link'},
            {'selector': '[href*="video"]', 'text': None, 'description': 'Video section link'},
            {'selector': '[href*="movies"]', 'text': None, 'description': 'Movies section link'},
            {'selector': '[href*="shows"]', 'text': None, 'description': 'Shows section link'},
            {'selector': '[href*="live"]', 'text': None, 'description': 'Live section link'},
            
            # Text-based navigation
            {'selector': 'a', 'text': 'Watch', 'description': 'Watch link'},
            {'selector': 'a', 'text': 'Videos', 'description': 'Videos link'},
            {'selector': 'a', 'text': 'Movies', 'description': 'Movies link'},
            {'selector': 'a', 'text': 'Shows', 'description': 'Shows link'},
            {'selector': 'a', 'text': 'Live', 'description': 'Live link'},
            {'selector': 'a', 'text': 'Stream', 'description': 'Stream link'},
            
            # Button-based navigation
            {'selector': 'button', 'text': 'Watch', 'description': 'Watch button'},
            {'selector': 'button', 'text': 'Videos', 'description': 'Videos button'},
            {'selector': 'button', 'text': 'Movies', 'description': 'Movies button'},
            {'selector': 'button', 'text': 'Shows', 'description': 'Shows button'},
            {'selector': 'button', 'text': 'Live', 'description': 'Live button'},
            
            # Sports-specific navigation
            {'selector': 'a', 'text': 'Sports', 'description': 'Sports link'},
            {'selector': 'a', 'text': 'Games', 'description': 'Games link'},
            {'selector': 'a', 'text': 'Highlights', 'description': 'Highlights link'},
            {'selector': 'a', 'text': 'Replays', 'description': 'Replays link'},
        ]
        
        for pattern in video_navigation_patterns:
            try:
                if pattern['text']:
                    # Text-based search
                    elements = page.locator(f"{pattern['selector']}:has-text('{pattern['text']}')")
                else:
                    # Selector-based search
                    elements = page.locator(pattern['selector'])
                
                if await elements.count() > 0:
                    logger.info(f"Found {pattern['description']}: {pattern['selector']}")
                    
                    # Try to click the element
                    try:
                        await elements.first.click()
                        logger.info(f"Clicked on {pattern['description']}")
                        
                        # Wait for navigation
                        await asyncio.sleep(2)
                        
                        # Check if we're on a new page with video content
                        current_url = page.url
                        logger.info(f"Current URL after navigation: {current_url}")
                        
                        # Check if page content changed significantly
                        try:
                            await page.wait_for_load_state('networkidle', timeout=5000)
                            logger.info(f"Successfully navigated to video content area: {current_url}")
                            return True
                        except:
                            pass
                            
                    except Exception as e:
                        logger.debug(f"Failed to click {pattern['description']}: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Pattern {pattern['description']} failed: {e}")
                continue
        
        logger.info("No video content areas found to navigate to")
        return False
        
    except Exception as e:
        logger.error(f"Error navigating to video content: {e}")
        return False


async def _trigger_video_from_thumbnails(page: Page, config) -> bool:
    """
    Try to trigger video content by clicking on video thumbnails or previews
    """
    try:
        logger.info("Looking for video thumbnails and previews...")
        
        # Common video thumbnail patterns
        thumbnail_patterns = [
            # Video thumbnails
            '[class*="thumbnail"]',
            '[class*="preview"]',
            '[class*="poster"]',
            '[class*="video"]',
            '[class*="player"]',
            '[class*="play"]',
            
            # Image elements that might be video thumbnails
            'img[src*="thumb"]',
            'img[src*="preview"]',
            'img[src*="poster"]',
            'img[src*="video"]',
            
            # Video-related containers
            '[data-video]',
            '[data-player]',
            '[data-src*="video"]',
            
            # Sports-specific patterns
            '[class*="highlight"]',
            '[class*="replay"]',
            '[class*="game"]',
            '[class*="match"]',
        ]
        
        for pattern in thumbnail_patterns:
            try:
                elements = page.locator(pattern)
                if await elements.count() > 0:
                    logger.info(f"Found potential video thumbnails with pattern: {pattern}")
                    
                    # Try clicking on the first few thumbnails
                    for i in range(min(3, await elements.count())):
                        try:
                            element = elements.nth(i)
                            
                            # Check if element is visible and clickable
                            if await element.is_visible():
                                logger.info(f"Clicking on thumbnail {i+1}")
                                await element.click()
                                
                                # Wait for potential video to load
                                await asyncio.sleep(2)
                                
                                # Check if video content appeared
                                video_check = await _detect_immediate_video_content(page, config)
                                if video_check:
                                    logger.info("Video content triggered from thumbnail!")
                                    return True
                                
                                # If no video, try to go back or continue
                                try:
                                    await page.go_back()
                                    await asyncio.sleep(1)
                                except:
                                    pass
                                    
                        except Exception as e:
                            logger.debug(f"Failed to click thumbnail {i+1}: {e}")
                            continue
                            
            except Exception as e:
                logger.debug(f"Thumbnail pattern {pattern} failed: {e}")
                continue
        
        logger.info("No video content triggered from thumbnails")
        return False
        
    except Exception as e:
        logger.error(f"Error triggering video from thumbnails: {e}")
        return False


async def wait_for_video_ready(page: Page, video_info: dict, config) -> bool:
    """
    Wait for video to be ready for playback
    
    Args:
        page: Playwright page object
        video_info: Video information dictionary
        config: VideoDetectionConfig object
        
    Returns:
        True if video is ready, False otherwise
    """
    try:
        if not video_info or not video_info['selector']:
            return False
        
        logger.info("Waiting for video to be ready...")
        
        # Wait for video element to be ready
        await page.locator(video_info['selector']).first.wait_for(state="visible", timeout=10000)
        
        # For native videos, wait for metadata
        if video_info['type'] == 'native':
            try:
                await page.locator(video_info['selector']).first.evaluate("""
                    el => {
                        return new Promise((resolve) => {
                            if (el.readyState >= 1) {
                                resolve();
                            } else {
                                el.addEventListener('loadedmetadata', resolve, { once: true });
                                el.addEventListener('error', resolve, { once: true });
                            }
                        });
                    }
                """)
                logger.info("Native video metadata loaded")
                return True
            except Exception as e:
                logger.debug(f"Error waiting for video metadata: {e}")
                return False
        
        # For embedded videos, just wait a bit
        elif video_info['type'] == 'embedded':
            await asyncio.sleep(config.video_load_wait)
            logger.info("Embedded video should be ready")
            return True
        
        # For custom players, try to find play button
        elif video_info['type'] == 'custom_player':
            try:
                play_button = page.locator(f"{video_info['selector']} {config.play_selectors[0]}")
                if await play_button.count() > 0:
                    await play_button.first.wait_for(state="visible", timeout=5000)
                    logger.info("Custom video player ready")
                    return True
            except Exception as e:
                logger.debug(f"Error checking custom player: {e}")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error waiting for video to be ready: {e}")
        return False 