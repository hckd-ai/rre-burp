"""
Core video discovery functionality using Playwright.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
import urllib.parse

from .models import VideoDiscoveryResult, VideoInfo, VideoType, VideoSource
from ..cookie_consent.cookie_handler import CookieConsentHandler
from ..cookie_consent.models import CookieConsentConfig
from ..config.site_explorer_config import SiteExplorerConfig


class VideoDiscoverer:
    """
    A focused video discovery service that finds video URLs from web pages.
    """
    
    def __init__(self, cookie_config: Optional[CookieConsentConfig] = None):
        self.cookie_config = cookie_config or CookieConsentConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        # Add timeout configuration
        self.timeout = 15  # Reduced to 15 seconds timeout for operations
        self.max_retries = 2  # Reduced maximum retries for operations
        
        # Initialize cookie consent handler with optimized settings for streaming sites
        self.cookie_config.timeout = 1000  # 1 second for consent handling
        self.cookie_config.aggressive_mode = True  # Skip visibility checks for speed
        self.cookie_config.max_attempts = 1  # Only try once to avoid delays
        self.cookie_config.wait_after_click = 0.2  # Minimal wait after clicking
        # Add Tubi TV specific selectors
        self.cookie_config.custom_selectors = [
            '[id*="onetrust"]',
            '[class*="onetrust"]',
            '[id*="cookiebot"]',
            '[class*="cookiebot"]',
            'button:has-text("Accept")',
            'button:has-text("Allow")',
            'button:has-text("Continue")',
            'button:has-text("Got it")',
            'button:has-text("OK")',
            '[aria-label*="Close"]',
            '[aria-label*="Accept"]',
            '[aria-label*="Allow"]'
        ]
        self.cookie_handler = CookieConsentHandler(self.cookie_config)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self):
        """Start the browser and create a new page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.page = await self.context.new_page()

    async def stop(self):
        """Stop the browser and clean up resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

    async def discover_videos(self, url: str, max_videos: int = 5) -> VideoDiscoveryResult:
        """Discover videos on a given URL."""
        start_time = time.time()
        
        try:
            # Set page timeout
            self.page.set_default_timeout(self.timeout * 1000)
            
            print(f"🔍 Starting video discovery for: {url}")
            print("=" * 60)
            
            # Navigate to the page
            await self.page.goto(url, wait_until='domcontentloaded')
            
            # Handle cookie consent and ads with minimal timeouts - non-blocking
            try:
                await asyncio.wait_for(self._handle_cookie_consent(), timeout=1.5)
            except asyncio.TimeoutError:
                print("⏰ Cookie consent handling timed out, continuing...")
            
            try:
                await asyncio.wait_for(self._handle_ads_and_overlays(), timeout=1.0)
            except asyncio.TimeoutError:
                print("⏰ Ad handling timed out, continuing...")
            
            # Quick scroll to load content - non-blocking
            try:
                await asyncio.wait_for(self._scroll_page_intelligently(), timeout=1.0)
            except asyncio.TimeoutError:
                print("⏰ Page scrolling timed out, continuing...")
            
            # Search for videos with remaining time
            remaining_timeout = self.timeout - 5  # Reserve 5 seconds for setup
            videos = await asyncio.wait_for(self._search_for_videos(), timeout=remaining_timeout)
            
            # Limit results
            videos = videos[:max_videos]
            
            exploration_time = time.time() - start_time
            
            if videos:
                print(f"✅ Discovery completed successfully in {exploration_time:.2f}s")
                print(f"📹 Found {len(videos)} videos")
                for i, video in enumerate(videos, 1):
                    print(f"\n🎬 Video {i}:")
                    print(f"   Title: {video.title or 'N/A'}")
                    print(f"   URL: {video.video_url}")
                    print(f"   Type: {video.video_type.value}")
                    print(f"   Source: {video.source.value}")
            else:
                print(f"✅ Discovery completed successfully in {exploration_time:.2f}s")
                print("📹 Found 0 videos")
                print("❌ No videos found on this page")
            
            return VideoDiscoveryResult(
                success=True,
                url=url,
                videos_found=videos,
                total_videos=len(videos),
                exploration_time=exploration_time
            )
            
        except asyncio.TimeoutError:
            exploration_time = time.time() - start_time
            print(f"⏰ Discovery timed out after {exploration_time:.2f}s")
            return VideoDiscoveryResult(
                success=False,
                url=url,
                videos_found=[],
                total_videos=0,
                exploration_time=exploration_time,
                error_message="Discovery timed out"
            )
        except Exception as e:
            exploration_time = time.time() - start_time
            print(f"❌ Discovery failed: {e}")
            return VideoDiscoveryResult(
                success=False,
                url=url,
                videos_found=[],
                total_videos=0,
                exploration_time=exploration_time,
                error_message=str(e)
            )

    async def _handle_cookie_consent(self):
        """Handle cookie consent using the dedicated handler with minimal timeout."""
        try:
            # Use a very short timeout for cookie consent to avoid blocking
            consent_handled = await asyncio.wait_for(
                self.cookie_handler.handle_consent(self.page, self.page.url), 
                timeout=2.0  # 2 second timeout for consent handling
            )
            if consent_handled:
                print("✅ Cookie consent handled successfully")
            else:
                print("ℹ️  No cookie consent dialog found")
        except asyncio.TimeoutError:
            print("⏰ Cookie consent handling timed out, continuing...")
        except Exception as e:
            print(f"⚠️ Cookie consent handling failed: {e}")
        # Always continue regardless of consent handling result
        print("🚀 Proceeding with video discovery...")

    async def _handle_ads_and_overlays(self):
        """Handle ads and overlays with minimal timeout."""
        try:
            # Look for common ad/overlay selectors with minimal timeouts
            selectors = [
                '[id*="skip"]',
                '[class*="skip"]',
                'button:has-text("Skip")',
                'a:has-text("Skip")',
                '[aria-label*="Skip"]',
                '[title*="Skip"]',
                'button[aria-label*="Close"]',
                'button[class*="close"]',
                'button[id*="close"]',
                '[class*="ad"] [aria-label*="Close"]',
                '[id*="ad"] [aria-label*="Close"]',
                '[id*="overlay"]',
                '[class*="overlay"]',
                '[id*="popup"]',
                '[class*="popup"]'
            ]
            
            for selector in selectors:
                try:
                    # Wait for element with very minimal timeout
                    element = await self.page.wait_for_selector(selector, timeout=200)  # Reduced to 200ms
                    if element:
                        await element.click()
                        print(f"✅ Closed ad/overlay: {selector}")
                        await asyncio.sleep(0.05)  # Very minimal wait
                        break
                except PlaywrightTimeoutError:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Ad/overlay handling failed: {e}")
        # Always continue regardless of ad handling result
        print("🚀 Proceeding with content loading...")

    async def _scroll_page_intelligently(self):
        """Scroll the page quickly to load content."""
        try:
            print("📜 Scrolling page to load content...")
            
            # Quick scroll down
            await self.page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(0.3)  # Very short delay
                    
            print("✅ Page scrolling completed")
            
        except Exception as e:
            print(f"⚠️ Page scrolling failed: {e}")

    async def _search_for_videos(self) -> List[VideoInfo]:
        """Search for video content on the page with streaming site optimizations."""
        videos = []
        
        print("🔍 Searching for video content...")
        
        # Collect ALL links first for pattern analysis
        all_links = []
        
        # Get all anchor tags
        link_elements = await self.page.query_selector_all('a[href]')
        for link in link_elements:
            try:
                href = await link.get_attribute('href')
                title = await link.text_content()
                if href and href.strip():
                    all_links.append({
                        'url': href.strip(),
                        'title': title.strip() if title else None,
                        'element': link
                    })
            except Exception:
                continue
        
        print(f"📊 Found {len(all_links)} total links for analysis")
        
        # Analyze URL patterns to identify video content
        video_patterns = self._analyze_video_patterns(all_links)
        print(f"🎯 Identified {len(video_patterns)} video-like patterns")
        
        # Look for native video elements
        video_elements = await self.page.query_selector_all('video')
        for video in video_elements:
            try:
                src = await video.get_attribute('src')
                if src:
                    videos.append(VideoInfo(
                        title="Native Video",
                        video_url=src,
                        video_type=VideoType.NATIVE,
                        source=VideoSource.NATIVE
                    ))
            except Exception:
                continue
        
        # Look for iframes (embedded videos) - common in streaming sites
        iframe_elements = await self.page.query_selector_all('iframe')
        for iframe in iframe_elements:
            try:
                src = await iframe.get_attribute('src')
                if src:
                    # Determine video type based on source
                    video_type = VideoType.CUSTOM_PLAYER
                    source = VideoSource.CUSTOM
                    
                    if 'youtube.com' in src or 'youtu.be' in src:
                        video_type = VideoType.YOUTUBE
                        source = VideoSource.YOUTUBE
                    elif 'vimeo.com' in src:
                        video_type = VideoType.VIMEO
                        source = VideoSource.VIMEO
                    elif 'dailymotion.com' in src:
                        video_type = VideoType.DAILYMOTION
                        source = VideoSource.DAILYMOTION
                    
                    videos.append(VideoInfo(
                        title="Embedded Video",
                        video_url=src,
                        video_type=video_type,
                        source=source
                    ))
            except Exception:
                continue
        
        # Process links based on pattern analysis
        for link_info in all_links:
            try:
                url = link_info['url']
                title = link_info['title']
                
                # Skip if no title or very short title
                if not title or len(title.strip()) < 2:
                    continue
                
                # Skip app store links and external links
                if self._is_app_store_link(url) or self._is_external_link(url):
                    continue
                
                # Check if this link matches video patterns
                if self._matches_video_pattern(url, video_patterns):
                    # Determine video type based on URL structure
                    video_type = VideoType.CUSTOM_PLAYER
                    source = VideoSource.CUSTOM
                    
                    # Check for specific streaming patterns
                    if '/movies/' in url or '/movie/' in url:
                        video_type = VideoType.MOVIE
                        source = VideoSource.STREAMING
                    elif '/tv/' in url or '/episode/' in url or '/series/' in url:
                        video_type = VideoType.TV_SHOW
                        source = VideoSource.STREAMING
                    elif '/watch/' in url or '/play/' in url or '/stream/' in url:
                        video_type = VideoType.CUSTOM_PLAYER
                        source = VideoSource.STREAMING
                    
                    videos.append(VideoInfo(
                        title=title,
                        video_url=url,
                        video_type=video_type,
                        source=source
                    ))
                    
            except Exception as e:
                continue
        
        # Sort videos by relevance score
        videos = self._sort_videos_by_relevance(videos, video_patterns)
        
        print(f"🎬 Found {len(videos)} potential video links after filtering")
        return videos
    
    def _analyze_video_patterns(self, links: List[dict]) -> List[str]:
        """Analyze URL patterns to identify video content patterns."""
        patterns = []
        url_counts = {}
        
        for link in links:
            url = link['url']
            if not url:
                continue
            
            # Skip external and app store links
            if self._is_external_link(url) or self._is_app_store_link(url):
                continue
            
            # Extract path segments
            try:
                parsed = urllib.parse.urlparse(url)
                path = parsed.path.strip('/')
                segments = path.split('/')
                
                # Look for video-related path patterns
                for i, segment in enumerate(segments):
                    if segment in ['movies', 'movie', 'tv', 'episode', 'series', 'watch', 'play', 'stream']:
                        # Create pattern with context
                        if i + 1 < len(segments):
                            pattern = f"/{segment}/{segments[i+1]}"
                            patterns.append(pattern)
                        
                        # Count URL structure
                        url_structure = '/'.join(segments[:i+2])
                        url_counts[url_structure] = url_counts.get(url_structure, 0) + 1
                        
            except Exception:
                continue
        
        # Return most common patterns
        sorted_patterns = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)
        return [pattern for pattern, count in sorted_patterns[:10]]  # Top 10 patterns
    
    def _is_app_store_link(self, url: str) -> bool:
        """Check if URL is an app store link."""
        app_store_domains = [
            'itunes.apple.com',
            'play.google.com',
            'apps.apple.com',
            'chrome.google.com',
            'microsoft.com/store',
            'amazon.com/apps'
        ]
        
        try:
            parsed = urllib.parse.urlparse(url)
            return any(domain in parsed.netloc for domain in app_store_domains)
        except:
            return False
    
    def _is_external_link(self, url: str) -> bool:
        """Check if URL is external to the current site."""
        try:
            parsed = urllib.parse.urlparse(url)
            current_domain = urllib.parse.urlparse(self.page.url).netloc
            
            # Check if it's a different domain
            if parsed.netloc and parsed.netloc != current_domain:
                return True
            
            # Check if it's a protocol-relative URL that would be external
            if url.startswith('//') and not url.startswith(f'//{current_domain}'):
                return True
                
            return False
        except:
            return False
    
    def _matches_video_pattern(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches identified video patterns."""
        try:
            parsed = urllib.parse.urlparse(url)
            path = parsed.path
            
            # Check if path matches any video patterns
            for pattern in patterns:
                if pattern in path:
                    return True
            
            # Additional video indicators
            video_indicators = ['/movies/', '/movie/', '/tv/', '/episode/', '/series/', '/watch/', '/play/', '/stream/']
            return any(indicator in path for indicator in video_indicators)
            
        except:
            return False
    
    def _sort_videos_by_relevance(self, videos: List[VideoInfo], patterns: List[str]) -> List[VideoInfo]:
        """Sort videos by relevance score based on pattern matching."""
        def calculate_relevance(video: VideoInfo) -> float:
            score = 0.0
            
            # Higher score for streaming content
            if video.source == VideoSource.STREAMING:
                score += 10.0
            
            # Higher score for movies and TV shows
            if video.video_type in [VideoType.MOVIE, VideoType.TV_SHOW]:
                score += 5.0
            
            # Higher score for URLs that match patterns
            for pattern in patterns:
                if pattern in video.video_url:
                    score += 3.0
            
            # Higher score for longer, more descriptive titles
            if video.title and len(video.title) > 10:
                score += 2.0
            
            # Lower score for very short titles
            if video.title and len(video.title) < 5:
                score -= 1.0
            
            return score
        
        # Sort by relevance score (highest first)
        return sorted(videos, key=calculate_relevance, reverse=True)

    def _detect_iframe_source(self, src: str) -> VideoSource:
        """Detect the source of an iframe."""
        src_lower = src.lower()
        if 'youtube.com' in src_lower or 'youtu.be' in src_lower:
            return VideoSource.YOUTUBE
        elif 'vimeo.com' in src_lower:
            return VideoSource.VIMEO
        elif 'dailymotion.com' in src_lower:
            return VideoSource.DAILYMOTION
        elif 'twitch.tv' in src_lower:
            return VideoSource.TWITCH
        else:
            return VideoSource.UNKNOWN

    async def _extract_video_title(self, element) -> Optional[str]:
        """Extract title from a video element."""
        try:
            # Try to get title from various attributes
            title = await element.get_attribute('title')
            if title:
                return title
                
            # Try to get alt text
            alt = await element.get_attribute('alt')
            if alt:
                return alt
                
            # Try to get aria-label
            aria_label = await element.get_attribute('aria-label')
            if aria_label:
                return aria_label
                
            return None
        except:
            return None

    async def _extract_iframe_title(self, iframe) -> Optional[str]:
        """Extract title from an iframe element."""
        try:
            # Try to get title from various attributes
            title = await iframe.get_attribute('title')
            if title:
                return title
                
            # Try to get aria-label
            aria_label = await iframe.get_attribute('aria-label')
            if aria_label:
                return aria_label
                
            return None
        except:
            return None 