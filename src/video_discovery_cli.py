#!/usr/bin/env python3
"""
CLI script for testing video discovery functionality.
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from video_discovery import VideoDiscoverer
from video_discovery.models import VideoDiscoveryResult


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Video Discovery CLI')
    parser.add_argument('url', help='URL to explore for videos')
    parser.add_argument('--max-videos', type=int, default=5, help='Maximum number of videos to find')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds for discovery operations')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Video Discovery CLI")
    print(f"🔗 URL: {args.url}")
    print(f"📹 Max Videos: {args.max_videos}")
    print(f"⏰ Timeout: {args.timeout}s")
    print("=" * 60)
    
    try:
        async with VideoDiscoverer() as discoverer:
            # Set custom timeout if provided
            if args.timeout != 30:
                discoverer.timeout = args.timeout
                
            # Run discovery with timeout
            result = await asyncio.wait_for(
                discoverer.discover_videos(args.url, args.max_videos),
                timeout=args.timeout + 10  # Add 10 seconds buffer
            )
            
            if result.success:
                print(f"\n✅ Discovery completed successfully!")
                print(f"📊 Total videos found: {result.total_videos}")
                print(f"⏱️  Time taken: {result.exploration_time:.2f}s")
            else:
                print(f"\n❌ Discovery failed: {result.error_message}")
                print(f"⏱️  Time taken: {result.exploration_time:.2f}s")
                
    except asyncio.TimeoutError:
        print(f"\n⏰ Discovery timed out after {args.timeout + 10}s")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Discovery interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Discovery failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  CLI interrupted by user")
        sys.exit(1) 