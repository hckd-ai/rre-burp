#!/usr/bin/env python3
"""
Test Video Detection Script
===========================

This script tests the enhanced video detection capabilities of the site explorer.
It demonstrates how to detect video content and analyze HAR files for video-related traffic.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from site_explorer.intelligent_explorer import IntelligentSiteExplorer
from config.site_explorer_config import load_config


async def test_video_detection():
    """Test video detection on a known video site"""
    
    # Test URLs with different types of video content
    test_sites = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # YouTube video
            "name": "YouTube Test"
        },
        {
            "url": "https://vimeo.com/148751763",  # Vimeo video
            "name": "Vimeo Test"
        },
        {
            "url": "https://www.tubi.tv/watch/123456",  # Tubi video (if available)
            "name": "Tubi Test"
        }
    ]
    
    config = load_config()
    config.headless = False  # Set to True for headless mode
    
    async with IntelligentSiteExplorer(config) as explorer:
        for test_site in test_sites:
            print(f"\n{'='*60}")
            print(f"Testing: {test_site['name']}")
            print(f"URL: {test_site['url']}")
            print(f"{'='*60}")
            
            try:
                result = await explorer.explore_site(test_site['url'], test_site['name'])
                
                # Print results
                print(f"\n✅ Success: {result['success']}")
                print(f"🎥 Video Found: {result.get('video_found', False)}")
                print(f"📁 HAR Collected: {result.get('har_collected', False)}")
                
                if result.get('video_found'):
                    print("\n🎬 Video Details:")
                    video_info = result.get('video_info', {})
                    print(f"  Type: {video_info.get('type', 'Unknown')}")
                    print(f"  Player: {video_info.get('player_type', 'Unknown')}")
                    print(f"  Title: {video_info.get('title', 'Unknown')}")
                    
                    if result.get('video_urls'):
                        print(f"  Video URLs: {len(result['video_urls'])}")
                        for i, url in enumerate(result['video_urls'][:3]):
                            print(f"    {i+1}. {url}")
                
                if result.get('har_analysis'):
                    har_analysis = result['har_analysis']
                    print(f"\n📊 HAR Analysis:")
                    print(f"  Total Requests: {har_analysis.get('total_requests', 0)}")
                    print(f"  Video-Related: {har_analysis.get('video_related_count', 0)}")
                    
                    if har_analysis.get('video_requests'):
                        print(f"  Video Files: {len(har_analysis['video_requests'])}")
                    if har_analysis.get('manifest_urls'):
                        print(f"  Manifests: {len(har_analysis['manifest_urls'])}")
                    if har_analysis.get('video_segments'):
                        print(f"  Video Segments: {len(har_analysis['video_segments'])}")
                
                if result.get('har_path'):
                    print(f"\n📁 HAR File: {result['har_path']}")
                
            except Exception as e:
                print(f"❌ Error testing {test_site['name']}: {e}")
                continue
            
            # Wait between tests
            await asyncio.sleep(2)
    
    # Print final statistics
    stats = explorer.get_stats()
    print(f"\n{'='*60}")
    print("FINAL STATISTICS")
    print(f"{'='*60}")
    print(f"Sites visited: {stats['sites_visited']}")
    print(f"Videos found: {stats['videos_found']}")
    print(f"HAR files collected: {stats['hars_collected']}")
    print(f"Errors encountered: {stats['errors_encountered']}")


async def test_har_analysis():
    """Test HAR analysis on existing HAR files"""
    
    har_dir = Path("collected_hars")
    if not har_dir.exists():
        print("No HAR files found in collected_hars directory")
        return
    
    har_files = list(har_dir.glob("*.har"))
    if not har_files:
        print("No HAR files found")
        return
    
    print(f"\n{'='*60}")
    print("HAR FILE ANALYSIS")
    print(f"{'='*60}")
    
    from utils.web_helpers import analyze_har_for_video_content
    
    for har_file in har_files:
        print(f"\n📁 Analyzing: {har_file.name}")
        try:
            analysis = await analyze_har_for_video_content(str(har_file))
            
            print(f"  Total Requests: {analysis.get('total_requests', 0)}")
            print(f"  Video-Related: {analysis.get('video_related_count', 0)}")
            
            if analysis.get('video_requests'):
                print(f"  Video Files: {len(analysis['video_requests'])}")
                for req in analysis['video_requests'][:3]:
                    print(f"    - {req['url']} ({req['content_type']})")
            
            if analysis.get('manifest_urls'):
                print(f"  Manifests: {len(analysis['manifest_urls'])}")
                for req in analysis['manifest_urls'][:3]:
                    print(f"    - {req['url']}")
            
            if analysis.get('video_segments'):
                print(f"  Video Segments: {len(analysis['video_segments'])}")
            
            if analysis.get('streaming_urls'):
                print(f"  Streaming URLs: {len(analysis['streaming_urls'])}")
            
            if analysis.get('ad_requests'):
                print(f"  Ad Requests: {len(analysis['ad_requests'])}")
                
        except Exception as e:
            print(f"  ❌ Error analyzing {har_file.name}: {e}")


async def main():
    """Main function"""
    print("Enhanced Video Detection Test")
    print("=" * 40)
    
    # Test HAR analysis on existing files first
    await test_har_analysis()
    
    # Ask user if they want to test live sites
    print(f"\n{'='*60}")
    response = input("Do you want to test live video detection? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        await test_video_detection()
    else:
        print("Skipping live tests. You can run them later with:")
        print("python src/examples/test_video_detection.py")


if __name__ == "__main__":
    asyncio.run(main()) 