"""
Site Explorer Configuration
==========================

Configuration settings for intelligent site exploration and HAR collection.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml
from pathlib import Path


@dataclass
class CookieConsentConfig:
    """Configuration for handling cookie consent dialogs"""
    
    # Common cookie consent selectors
    selectors: List[str] = None
    # Common button text patterns
    button_texts: List[str] = None
    # Wait time after consent
    wait_after_consent: float = 2.0
    
    def __post_init__(self):
        if self.selectors is None:
            self.selectors = [
                '[id*="cookie"]',
                '[class*="cookie"]',
                '[id*="consent"]',
                '[class*="consent"]',
                '[id*="gdpr"]',
                '[class*="gdpr"]',
                '[id*="privacy"]',
                '[class*="privacy"]',
                'div[role="dialog"]',
                'div[role="alertdialog"]'
            ]
        
        if self.button_texts is None:
            self.button_texts = [
                "Accept",
                "Accept All",
                "Allow All",
                "I Accept",
                "OK",
                "Continue",
                "Got it",
                "Close",
                "×",
                "Accept cookies",
                "Accept all cookies"
            ]


@dataclass
class AdHandlingConfig:
    """Configuration for handling advertisements and overlays"""
    
    # Selectors for common ad elements
    ad_selectors: List[str] = None
    # Selectors for skip buttons
    skip_selectors: List[str] = None
    # Maximum wait time for ads
    max_ad_wait: float = 30.0
    # Wait time after skipping ads
    wait_after_skip: float = 1.0
    
    def __post_init__(self):
        if self.ad_selectors is None:
            self.ad_selectors = [
                '[id*="ad"]',
                '[class*="ad"]',
                '[id*="banner"]',
                '[class*="banner"]',
                '[id*="overlay"]',
                '[class*="overlay"]',
                '[id*="popup"]',
                '[class*="popup"]',
                'iframe[src*="ads"]',
                'iframe[src*="doubleclick"]',
                'iframe[src*="googlesyndication"]'
            ]
        
        if self.skip_selectors is None:
            self.skip_selectors = [
                '[id*="skip"]',
                '[class*="skip"]',
                'button:contains("Skip")',
                'a:contains("Skip")',
                '[aria-label*="Skip"]',
                '[title*="Skip"]'
            ]


@dataclass
class VideoDetectionConfig:
    """Configuration for detecting and interacting with video content"""
    
    # Video element selectors
    video_selectors: List[str] = None
    # Video player selectors
    player_selectors: List[str] = None
    # Play button selectors
    play_selectors: List[str] = None
    # Wait time for video to load
    video_load_wait: float = 5.0
    # Minimum video duration to consider
    min_video_duration: float = 10.0
    # Enable intelligent video navigation
    enable_video_navigation: bool = True
    # Enable thumbnail triggering
    enable_thumbnail_triggering: bool = True
    # Maximum navigation attempts
    max_navigation_attempts: int = 3
    # Wait time after navigation
    navigation_wait_time: float = 3.0
    
    def __post_init__(self):
        if self.video_selectors is None:
            self.video_selectors = [
                'video',
                '[data-video]',
                '[class*="video"]',
                '[id*="video"]',
                'iframe[src*="youtube"]',
                'iframe[src*="vimeo"]',
                'iframe[src*="dailymotion"]',
                # Streaming service specific
                '[class*="stream"]',
                '[class*="live"]',
                '[class*="broadcast"]',
                '[class*="feed"]',
                '[class*="channel"]',
                # Sports streaming
                '[class*="game"]',
                '[class*="match"]',
                '[class*="highlight"]',
                '[class*="replay"]',
                '[class*="coverage"]',
                # Video containers
                '[class*="video-container"]',
                '[class*="media-container"]',
                '[class*="player-container"]',
                '[data-player-type]',
                '[data-media-type="video"]'
            ]
        
        if self.player_selectors is None:
            self.player_selectors = [
                '[class*="player"]',
                '[id*="player"]',
                '[class*="video-player"]',
                '[id*="video-player"]',
                '[class*="media-player"]',
                '[id*="media-player"]',
                # Streaming specific players
                '[class*="stream-player"]',
                '[class*="live-player"]',
                '[class*="broadcast-player"]',
                '[class*="tv-player"]',
                '[class*="channel-player"]',
                # Sports players
                '[class*="game-player"]',
                '[class*="match-player"]',
                '[class*="highlight-player"]',
                '[class*="replay-player"]',
                # Generic media players
                '[class*="html5-player"]',
                '[class*="flash-player"]',
                '[class*="jwplayer"]',
                '[class*="videojs"]',
                '[class*="plyr"]',
                '[class*="shaka"]',
                # Data attributes
                '[data-player]',
                '[data-player-type]',
                '[data-media-player]'
            ]
        
        if self.play_selectors is None:
            self.play_selectors = [
                '[class*="play"]',
                '[id*="play"]',
                '[aria-label*="Play"]',
                '[title*="Play"]',
                'button[class*="play"]',
                'button[id*="play"]',
                # Streaming specific play buttons
                '[class*="play-button"]',
                '[class*="play-btn"]',
                '[class*="start-stream"]',
                '[class*="start-broadcast"]',
                '[class*="watch-now"]',
                '[class*="watch-live"]',
                '[class*="start-watching"]',
                # Sports specific
                '[class*="watch-game"]',
                '[class*="watch-match"]',
                '[class*="watch-highlight"]',
                '[class*="watch-replay"]',
                # Icon-based play buttons
                '[class*="play-icon"]',
                '[class*="triangle"]',
                '[class*="play-triangle"]',
                # Text-based play buttons
                'button:contains("Play")',
                'button:contains("Watch")',
                'button:contains("Start")',
                'button:contains("Stream")',
                'button:contains("Live")',
                'a:contains("Play")',
                'a:contains("Watch")',
                'a:contains("Start")',
                'a:contains("Stream")',
                'a:contains("Live")'
            ]


@dataclass
class SiteExplorerConfig:
    """Main configuration for site exploration"""
    
    # Browser settings
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Timing settings
    page_load_timeout: float = 30.0
    navigation_timeout: float = 20.0
    wait_for_stable: float = 3.0
    scroll_pause: float = 1.0
    
    # Interaction settings
    max_scroll_attempts: int = 5
    click_retry_attempts: int = 3
    hover_delay: float = 0.5
    
    # Cookie consent handling
    cookie_consent: CookieConsentConfig = None
    
    # Ad handling
    ad_handling: AdHandlingConfig = None
    
    # Video detection
    video_detection: VideoDetectionConfig = None
    
    # HAR collection
    har_output_dir: str = "collected_hars"
    har_filename_template: str = "{site_name}_{timestamp}.har"
    
    def __post_init__(self):
        if self.cookie_consent is None:
            self.cookie_consent = CookieConsentConfig()
        if self.ad_handling is None:
            self.ad_handling = AdHandlingConfig()
        if self.video_detection is None:
            self.video_detection = VideoDetectionConfig()


def load_config(config_path: Optional[str] = None) -> SiteExplorerConfig:
    """Load configuration from YAML file or use defaults"""
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        # Merge with defaults
        config = SiteExplorerConfig()
        
        # Update with loaded values
        for key, value in config_data.items():
            if hasattr(config, key):
                if isinstance(value, dict) and hasattr(config, key):
                    # Handle nested configs
                    nested_config = getattr(config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(config, key, value)
        
        return config
    
    return SiteExplorerConfig()


def save_config(config: SiteExplorerConfig, config_path: str) -> None:
    """Save configuration to YAML file"""
    
    config_dict = {
        'headless': config.headless,
        'viewport_width': config.viewport_width,
        'viewport_height': config.viewport_height,
        'user_agent': config.user_agent,
        'page_load_timeout': config.page_load_timeout,
        'navigation_timeout': config.navigation_timeout,
        'wait_for_stable': config.wait_for_stable,
        'scroll_pause': config.scroll_pause,
        'max_scroll_attempts': config.max_scroll_attempts,
        'click_retry_attempts': config.click_retry_attempts,
        'hover_delay': config.hover_delay,
        'har_output_dir': config.har_output_dir,
        'har_filename_template': config.har_filename_template,
        'cookie_consent': {
            'selectors': config.cookie_consent.selectors,
            'button_texts': config.cookie_consent.button_texts,
            'wait_after_consent': config.cookie_consent.wait_after_consent
        },
        'ad_handling': {
            'ad_selectors': config.ad_handling.ad_selectors,
            'skip_selectors': config.ad_handling.skip_selectors,
            'max_ad_wait': config.ad_handling.max_ad_wait,
            'wait_after_skip': config.ad_handling.wait_after_skip
        },
        'video_detection': {
            'video_selectors': config.video_detection.video_selectors,
            'player_selectors': config.video_detection.player_selectors,
            'play_selectors': config.video_detection.play_selectors,
            'video_load_wait': config.video_detection.video_load_wait,
            'min_video_duration': config.video_detection.min_video_duration
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2) 