"""
Video Discovery Module

A focused module for discovering video URLs from web pages.
"""

from .video_discoverer import VideoDiscoverer
from .models import VideoDiscoveryResult, VideoInfo

__all__ = ["VideoDiscoverer", "VideoDiscoveryResult", "VideoInfo"] 