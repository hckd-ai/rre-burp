#!/usr/bin/env python3
"""
Test script for video discovery functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from video_discovery import VideoDiscoverer

async def test_video_discovery():
    """Test the video discovery on a few sample URLs."""
    
    test_urls = [
        "https://www.youtube.com",
        "https://www.vimeo.com",
        "https://www.tubi.tv",
        "https://www.espn.com/watch"
    ]
    
    print("🧪 Testing Video Discovery Service")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        print("-" * 40)
        
        try:
            async with VideoDiscoverer() as discoverer:
                result = await discoverer.discover_videos(url)
                
                if result.success:
                    print(f"✅ Success: Found {result.total_videos} videos in {result.exploration_time:.2f}s")
                    
                    if result.videos_found:
                        for i, video in enumerate(result.videos_found[:3], 1):  # Show first 3
                            print(f"  🎬 {i}. {video.title or 'Untitled'}")
                            print(f"     Type: {video.video_type.value}")
                            print(f"     Source: {video.source.value}")
                            print(f"     URL: {video.video_url[:80]}...")
                    else:
                        print("  ❌ No videos found")
                else:
                    print(f"❌ Failed: {result.error_message}")
                    
        except Exception as e:
            print(f"💥 Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_video_discovery()) 