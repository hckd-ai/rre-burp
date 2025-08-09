"""
Utilities Package
================

Common utility functions and helpers.
"""

from .web_helpers import (
    wait_for_page_stable,
    find_and_click_element,
    handle_cookie_consent,
    handle_ads_and_overlays,
    scroll_page_intelligently,
    detect_video_content,
    wait_for_video_ready
)

__all__ = [
    'wait_for_page_stable',
    'find_and_click_element',
    'handle_cookie_consent',
    'handle_ads_and_overlays',
    'scroll_page_intelligently',
    'detect_video_content',
    'wait_for_video_ready'
] 