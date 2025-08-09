"""
Data models for video discovery results.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class VideoType(Enum):
    """Types of video content that can be discovered."""
    NATIVE = "native"
    EMBEDDED = "embedded"
    STREAMING = "streaming"
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    CUSTOM_PLAYER = "custom_player"
    UNKNOWN = "unknown"


class VideoSource(Enum):
    """Sources of video content."""
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    TWITCH = "twitch"
    NATIVE = "native"
    CUSTOM = "custom"
    STREAMING = "streaming"
    UNKNOWN = "unknown"


@dataclass
class VideoInfo:
    """Information about a discovered video."""
    title: Optional[str]
    video_url: str
    video_type: VideoType
    source: VideoSource
    player_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class VideoDiscoveryResult:
    """Result of video discovery operation."""
    success: bool
    url: str
    videos_found: List[VideoInfo]
    total_videos: int
    exploration_time: float
    error_message: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None 