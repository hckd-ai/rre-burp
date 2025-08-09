"""
FastAPI routes for video discovery service.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio
import logging

from ..video_discovery.video_discoverer import VideoDiscoverer
from ..video_discovery.models import VideoDiscoveryResult, VideoInfo, VideoType, VideoSource
from ..config.site_explorer_config import SiteExplorerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class VideoDiscoveryRequest(BaseModel):
    url: HttpUrl
    max_videos: int = 10
    timeout: int = 15
    headless: bool = True

class VideoDiscoveryResponse(BaseModel):
    success: bool
    url: str
    videos_found: List[dict]
    total_videos: int
    exploration_time: float
    error_message: Optional[str] = None
    debug_info: Optional[dict] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        message="Video Discovery API is running",
        timestamp=datetime.utcnow().isoformat()
    )

@router.post("/discover", response_model=VideoDiscoveryResponse)
async def discover_videos(request: VideoDiscoveryRequest):
    """
    Discover videos on a given URL.
    
    Args:
        request: VideoDiscoveryRequest containing URL and parameters
        
    Returns:
        VideoDiscoveryResponse with discovered videos
    """
    try:
        logger.info(f"Starting video discovery for: {request.url}")
        
        # Create configuration
        config = SiteExplorerConfig(
            headless=request.headless,
            page_load_timeout=request.timeout,
            navigation_timeout=request.timeout
        )
        
        # Create video discoverer
        async with VideoDiscoverer() as discoverer:
            # Discover videos
            result = await discoverer.discover_videos(str(request.url), max_videos=request.max_videos)
        
        # Convert VideoInfo objects to dictionaries for JSON response
        videos_dict = []
        for video in result.videos_found:
            video_dict = {
                "title": video.title,
                "video_url": video.video_url,
                "video_type": video.video_type.value,
                "source": video.source.value,
                "player_url": video.player_url,
                "thumbnail_url": video.thumbnail_url,
                "duration": video.duration,
                "description": video.description,
                "metadata": video.metadata
            }
            videos_dict.append(video_dict)
        
        # Create response
        response = VideoDiscoveryResponse(
            success=result.success,
            url=str(request.url),  # Convert HttpUrl to string
            videos_found=videos_dict,
            total_videos=len(videos_dict),
            exploration_time=result.exploration_time,
            error_message=result.error_message,
            debug_info=result.debug_info
        )
        
        logger.info(f"Video discovery completed successfully. Found {result.total_videos} videos.")
        return response
        
    except Exception as e:
        logger.error(f"Video discovery failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Video discovery failed: {str(e)}"
        )

@router.get("/discover/{url:path}")
async def discover_videos_get(
    url: str,
    max_videos: int = 10,
    timeout: int = 15,
    headless: bool = True
):
    """
    Discover videos using GET request (alternative to POST).
    
    Args:
        url: URL to discover videos on
        max_videos: Maximum number of videos to return
        timeout: Timeout in seconds
        headless: Whether to run browser in headless mode
        
    Returns:
        VideoDiscoveryResponse with discovered videos
    """
    # Convert to POST request format
    request = VideoDiscoveryRequest(
        url=url,
        max_videos=max_videos,
        timeout=timeout,
        headless=headless
    )
    
    return await discover_videos(request)

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Video Discovery API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "discover": "/discover",
            "discover_get": "/discover/{url}"
        },
        "usage": {
            "POST /discover": "Discover videos with JSON payload",
            "GET /discover/{url}": "Discover videos with URL parameters",
            "GET /health": "Health check"
        }
    } 