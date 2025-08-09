"""
Configuration Package
===================

Configuration management and settings.
"""

from .site_explorer_config import (
    SiteExplorerConfig,
    CookieConsentConfig,
    AdHandlingConfig,
    VideoDetectionConfig,
    load_config,
    save_config
)

__all__ = [
    'SiteExplorerConfig',
    'CookieConsentConfig',
    'AdHandlingConfig',
    'VideoDetectionConfig',
    'load_config',
    'save_config'
] 