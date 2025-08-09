"""
Intelligent Site Explorer
========================

Main class for intelligently exploring websites, finding video content,
and collecting HAR files for analysis.
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ..config.site_explorer_config import SiteExplorerConfig, load_config
from ..utils.web_helpers import (
    wait_for_page_stable,
    handle_cookie_consent,
    handle_ads_and_overlays,
    scroll_page_intelligently,
    detect_video_content,
    wait_for_video_ready,
    find_and_click_element
)

logger = logging.getLogger(__name__)


class IntelligentSiteExplorer:
    """
    Intelligent site explorer that can navigate websites, handle common obstacles,
    find video content, and collect HAR files for analysis.
    """
    
    def __init__(self, config: Optional[SiteExplorerConfig] = None, config_path: Optional[str] = None):
        """
        Initialize the site explorer
        
        Args:
            config: Configuration object
            config_path: Path to configuration file
        """
        self.config = config or load_config(config_path)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Ensure output directory exists
        self.har_output_dir = Path(self.config.har_output_dir)
        self.har_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'sites_visited': 0,
            'videos_found': 0,
            'hars_collected': 0,
            'errors': 0,
            'start_time': None,
            'total_time': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
    
    async def start(self):
        """Start the browser and create context"""
        try:
            logger.info("Starting Playwright browser...")
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create context with HAR recording
            self.context = await self.browser.new_context(
                viewport={'width': self.config.viewport_width, 'height': self.config.viewport_height},
                user_agent=self.config.user_agent,
                record_har_path=None,  # We'll set this per page
                record_video_dir=None,
                ignore_https_errors=True
            )
            
            logger.info("Browser started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def stop(self):
        """Stop the browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
    
    async def explore_site(self, url: str, site_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Explore a site and find video content
        
        Args:
            url: URL to explore
            site_name: Optional name for the site (used in HAR filename)
            
        Returns:
            Dictionary with exploration results
        """
        if not site_name:
            site_name = urlparse(url).netloc
        
        self.stats['sites_visited'] += 1
        start_time = time.time()
        
        logger.info(f"Starting exploration of {site_name} ({url})")
        
        result = {
            'site_name': site_name,
            'url': url,
            'success': False,
            'video_found': False,
            'har_collected': False,
            'har_path': None,
            'video_info': None,
            'video_page_url': None,  # URL where video was actually found
            'video_source_url': None,  # Direct video source URL
            'navigation_history': [],  # Track navigation steps
            'errors': [],
            'exploration_time': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Create new page with HAR recording
            har_filename = self.config.har_filename_template.format(
                site_name=site_name.replace('.', '_'),
                timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            har_path = self.har_output_dir / har_filename
            
            self.page = await self.context.new_page()
            await self.context.route("**/*", lambda route: route.continue_())
            
            # Start HAR recording
            await self.context.route("**/*", lambda route: route.continue_())
            
            # Navigate to the site
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=self.config.page_load_timeout * 1000)
            
            # Wait for page to be stable
            await wait_for_page_stable(self.page, timeout=self.config.wait_for_stable)
            
            # Handle cookie consent
            logger.info("Handling cookie consent...")
            await handle_cookie_consent(self.page, self.config.cookie_consent)
            
            # Handle ads and overlays
            logger.info("Handling ads and overlays...")
            await handle_ads_and_overlays(self.page, self.config.ad_handling)
            
            # Scroll to load dynamic content
            logger.info("Scrolling page to load content...")
            await scroll_page_intelligently(self.page, self.config)
            
            # Wait for page to be stable again
            await wait_for_page_stable(self.page, timeout=self.config.wait_for_stable)
            
            # Look for video content
            logger.info("Searching for video content...")
            video_info = await detect_video_content(self.page, self.config.video_detection)
            
            if video_info:
                logger.info(f"Video found: {video_info}")
                result['video_found'] = True
                result['video_info'] = video_info
                
                # Store video URL information
                if 'page_url' in video_info:
                    result['video_page_url'] = video_info['page_url']
                    logger.info(f"Video found on page: {video_info['page_url']}")
                
                if 'video_url' in video_info and video_info['video_url']:
                    result['video_source_url'] = video_info['video_url']
                    logger.info(f"Video source URL: {video_info['video_url']}")
                
                if 'navigation_history' in video_info:
                    result['navigation_history'] = video_info['navigation_history']
                    logger.info(f"Navigation history: {video_info['navigation_history']}")
                
                # Wait for video to be ready
                if await wait_for_video_ready(self.page, video_info, self.config.video_detection):
                    logger.info("Video is ready for playback")
                    
                    # Try to start video playback
                    if video_info['type'] == 'native':
                        try:
                            await self.page.locator(video_info['selector']).first.evaluate("el => el.play()")
                            logger.info("Started native video playback")
                        except Exception as e:
                            logger.debug(f"Could not start video playback: {e}")
                    
                    elif video_info['type'] == 'custom_player':
                        # Try to click play button
                        play_clicked = await find_and_click_element(
                            self.page,
                            [f"{video_info['selector']} {self.config.video_detection.play_selectors[0]}"],
                            max_attempts=2
                        )
                        if play_clicked:
                            logger.info("Clicked play button on custom player")
                    
                    # Wait for video to play for a bit
                    await asyncio.sleep(5)
                    
                    # Collect HAR file with enhanced video detection
                    logger.info("Collecting HAR file with video traffic...")
                    
                    # Start HAR recording if not already started
                    if not hasattr(self.context, '_har_recording'):
                        await self.context.route("**/*", lambda route: route.continue_())
                        await self.context.start_har_recording(
                            path=str(har_path),
                            content="embed"  # Include response bodies
                        )
                        self.context._har_recording = True
                    
                    # Wait for additional video-related requests
                    logger.info("Waiting for video-related network requests...")
                    await asyncio.sleep(10)  # Wait for video segments, manifests, etc.
                    
                    # Stop HAR recording and save
                    if hasattr(self.context, '_har_recording'):
                        har_data = await self.context.stop_har_recording()
                        with open(har_path, 'w') as f:
                            import json
                            json.dump(har_data, f, indent=2)
                        delattr(self.context, '_har_recording')
                    
                    result['har_collected'] = True
                    result['har_path'] = str(har_path)
                    result['video_urls'] = video_info.get('video_urls', [])
                    result['stream_urls'] = video_info.get('stream_urls', [])
                    result['manifest_urls'] = video_info.get('manifest_urls', [])
                    
                    self.stats['hars_collected'] += 1
                    self.stats['videos_found'] += 1
                    
                    logger.info(f"HAR file collected: {har_path}")
                    if video_info.get('video_urls'):
                        logger.info(f"Video URLs captured: {video_info['video_urls']}")
                    if video_info.get('stream_urls'):
                        logger.info(f"Streaming URLs captured: {video_info['stream_urls']}")
                
                    # Analyze HAR file for additional video content
                    logger.info("Analyzing HAR file for video-related network traffic...")
                    from src.utils.web_helpers import analyze_har_for_video_content
                    har_analysis = await analyze_har_for_video_content(har_path)
                    
                    if har_analysis.get('video_related_count', 0) > 0:
                        logger.info(f"Found {har_analysis['video_related_count']} video-related network requests")
                        if har_analysis.get('video_requests'):
                            logger.info(f"Video files: {len(har_analysis['video_requests'])}")
                        if har_analysis.get('manifest_urls'):
                            logger.info(f"Manifests: {len(har_analysis['manifest_urls'])}")
                        if har_analysis.get('video_segments'):
                            logger.info(f"Video segments: {len(har_analysis['video_segments'])}")
                        
                        # Update result with HAR analysis
                        result['har_analysis'] = har_analysis
                    else:
                        logger.info("No additional video-related network traffic found in HAR")
                else:
                    logger.warning("Video was not ready for playback")
            else:
                logger.info("No video content found on this page")
                
                # Still collect HAR for analysis
                logger.info("Collecting HAR file for page analysis...")
                
                # Start HAR recording if not already started
                if not hasattr(self.context, '_har_recording'):
                    await self.context.route("**/*", lambda route: route.continue_())
                    await self.context.start_har_recording(
                        path=str(har_path),
                        content="embed"  # Include response bodies
                    )
                    self.context._har_recording = True
                
                # Wait for any dynamic content
                await asyncio.sleep(5)
                
                # Stop HAR recording and save
                if hasattr(self.context, '_har_recording'):
                    har_data = await self.context.stop_har_recording()
                    with open(har_path, 'w') as f:
                        import json
                        json.dump(har_data, f, indent=2)
                    delattr(self.context, '_har_recording')
                
                result['har_collected'] = True
                result['har_path'] = str(har_path)
                self.stats['hars_collected'] += 1
                
                # Analyze HAR file for potential video content
                logger.info("Analyzing HAR file for potential video content...")
                from src.utils.web_helpers import analyze_har_for_video_content
                har_analysis = await analyze_har_for_video_content(har_path)
                
                if har_analysis.get('video_related_count', 0) > 0:
                    logger.info(f"Found {har_analysis['video_related_count']} video-related network requests in HAR")
                    result['har_analysis'] = har_analysis
                    
                    # Check if we found video content in the HAR that we missed during page analysis
                    if har_analysis.get('video_requests') or har_analysis.get('manifest_urls'):
                        logger.info("Video content detected in network traffic - updating result")
                        result['video_found'] = True
                        result['video_detected_in_har'] = True
                        
                        # Extract video URLs from HAR analysis
                        video_urls = []
                        if har_analysis.get('video_requests'):
                            video_urls.extend([req['url'] for req in har_analysis['video_requests']])
                        if har_analysis.get('manifest_urls'):
                            video_urls.extend([req['url'] for req in har_analysis['manifest_urls']])
                        
                        result['video_urls'] = video_urls
                        result['video_url'] = video_urls[0] if video_urls else None
                        
                        self.stats['videos_found'] += 1
                else:
                    logger.info("No video-related network traffic found in HAR")
            
            result['success'] = True
            
        except PlaywrightTimeoutError as e:
            error_msg = f"Timeout error: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Exploration error: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            self.stats['errors'] += 1
            
        finally:
            # Cleanup page
            if self.page:
                await self.page.close()
                self.page = None
        
        # Calculate exploration time
        exploration_time = time.time() - start_time
        result['exploration_time'] = exploration_time
        
        logger.info(f"Exploration of {site_name} completed in {exploration_time:.2f}s")
        return result
    
    async def explore_multiple_sites(self, urls: List[str], site_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Explore multiple sites
        
        Args:
            urls: List of URLs to explore
            site_names: Optional list of site names
            
        Returns:
            List of exploration results
        """
        if site_names and len(site_names) != len(urls):
            raise ValueError("Number of site names must match number of URLs")
        
        results = []
        
        for i, url in enumerate(urls):
            site_name = site_names[i] if site_names else None
            
            try:
                result = await self.explore_site(url, site_name)
                results.append(result)
                
                # Small delay between sites
                if i < len(urls) - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Failed to explore {url}: {e}")
                results.append({
                    'site_name': site_name or urlparse(url).netloc,
                    'url': url,
                    'success': False,
                    'video_found': False,
                    'har_collected': False,
                    'har_path': None,
                    'video_info': None,
                    'errors': [str(e)],
                    'exploration_time': 0,
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get exploration statistics"""
        if self.stats['start_time']:
            self.stats['total_time'] = time.time() - self.stats['start_time']
        
        return self.stats.copy()
    
    def print_stats(self):
        """Print exploration statistics"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("EXPLORATION STATISTICS")
        print("="*50)
        print(f"Sites visited: {stats['sites_visited']}")
        print(f"Videos found: {stats['videos_found']}")
        print(f"HAR files collected: {stats['hars_collected']}")
        print(f"Errors encountered: {stats['errors']}")
        if stats['total_time'] > 0:
            print(f"Total exploration time: {stats['total_time']:.2f}s")
        print("="*50)


async def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python intelligent_explorer.py <url> [site_name]")
        return
    
    url = sys.argv[1]
    site_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load test sites if URL is 'test'
    if url == 'test':
        import json
        with open('test_sites.json', 'r') as f:
            test_data = json.load(f)
        
        urls = [site['url'] for site in test_data['test_sites'][:3]]  # Test first 3 sites
        site_names = [site['name'] for site in test_data['test_sites'][:3]]
        
        async with IntelligentSiteExplorer() as explorer:
            results = await explorer.explore_multiple_sites(urls, site_names)
            
            for result in results:
                print(f"\nSite: {result['site_name']}")
                print(f"URL: {result['url']}")
                print(f"Success: {result['success']}")
                print(f"Video found: {result['video_found']}")
                print(f"HAR collected: {result['har_collected']}")
                if result['har_path']:
                    print(f"HAR path: {result['har_path']}")
                if result['errors']:
                    print(f"Errors: {result['errors']}")
            
            explorer.print_stats()
    else:
        # Single site exploration
        async with IntelligentSiteExplorer() as explorer:
            result = await explorer.explore_site(url, site_name)
            
            # Print detailed results
            print("=" * 60)
            print(f"EXPLORATION RESULTS: {site_name}")
            print("=" * 60)
            print(f"URL: {url}")
            print(f"Success: {'✅' if result['success'] else '❌'}")
            print(f"Video Found: {'✅' if result.get('video_found') else '❌'}")
            print(f"HAR Collected: {'✅' if result.get('har_collected') else '❌'}")
            print(f"Exploration Time: {result.get('exploration_time', 0):.2f}s")
            
            if result.get('har_path'):
                print(f"HAR File: {result['har_path']}")
            
            # Show video information
            if result.get('video_found'):
                print("\n🎥 VIDEO DETECTION DETAILS:")
                if result.get('video_info'):
                    video_info = result['video_info']
                    print(f"  Type: {video_info.get('type', 'Unknown')}")
                    print(f"  Player: {video_info.get('player_type', 'Unknown')}")
                    if video_info.get('title'):
                        print(f"  Title: {video_info['title']}")
                    if video_info.get('duration'):
                        print(f"  Duration: {video_info['duration']:.1f}s")
                    if video_info.get('video_urls'):
                        print(f"  Video URLs: {len(video_info['video_urls'])} found")
                        for i, url in enumerate(video_info['video_urls'][:3]):  # Show first 3
                            print(f"    {i+1}. {url}")
                        if len(video_info['video_urls']) > 3:
                            print(f"    ... and {len(video_info['video_urls']) - 3} more")
                
                if result.get('video_detected_in_har'):
                    print("  📡 Video detected in network traffic (HAR analysis)")
                
                if result.get('video_urls'):
                    print(f"  Total Video URLs: {len(result['video_urls'])}")
            
            # Show HAR analysis results
            if result.get('har_analysis'):
                har_analysis = result['har_analysis']
                print(f"\n📊 HAR ANALYSIS:")
                print(f"  Total Requests: {har_analysis.get('total_requests', 0)}")
                print(f"  Video-Related: {har_analysis.get('video_related_count', 0)}")
                
                if har_analysis.get('video_requests'):
                    print(f"  Video Files: {len(har_analysis['video_requests'])}")
                if har_analysis.get('manifest_urls'):
                    print(f"  Manifests: {len(har_analysis['manifest_urls'])}")
                if har_analysis.get('video_segments'):
                    print(f"  Video Segments: {len(har_analysis['video_segments'])}")
                if har_analysis.get('streaming_urls'):
                    print(f"  Streaming URLs: {len(har_analysis['streaming_urls'])}")
                if har_analysis.get('ad_requests'):
                    print(f"  Ad Requests: {len(har_analysis['ad_requests'])}")
            
            # Show navigation history if available
            if result.get('navigation_history'):
                print(f"\n🧭 NAVIGATION HISTORY:")
                for i, step in enumerate(result['navigation_history']):
                    print(f"  {i+1}. {step}")
            
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 