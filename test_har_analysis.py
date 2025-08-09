#!/usr/bin/env python3
"""
Simple HAR Analysis Test
========================

This script tests the HAR analysis functionality on existing HAR files.
"""

import asyncio
import json
import sys
from pathlib import Path


async def analyze_har_for_video_content(har_path: str) -> dict:
    """
    Analyze a HAR file to extract video-related network traffic and URLs
    
    Args:
        har_path: Path to the HAR file
        
    Returns:
        Dictionary with video analysis results
    """
    try:
        with open(har_path, 'r') as f:
            har_data = json.load(f)
        
        video_analysis = {
            'video_requests': [],
            'streaming_urls': [],
            'manifest_urls': [],
            'video_segments': [],
            'ad_requests': [],
            'total_requests': 0,
            'video_related_count': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return video_analysis
        
        entries = har_data['log']['entries']
        video_analysis['total_requests'] = len(entries)
        
        # Video file extensions
        video_extensions = ['.mp4', '.webm', '.ogg', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
        # Streaming formats
        streaming_formats = ['.m3u8', '.mpd', '.ts', '.m4s', '.mp4', '.webm']
        # Manifest patterns
        manifest_patterns = ['manifest', 'playlist', 'index', 'master', 'live']
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            
            # Check if this is a video-related request
            is_video_related = False
            
            # Check for video file extensions
            if any(ext in url.lower() for ext in video_extensions):
                is_video_related = True
                video_analysis['video_requests'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'size': response.get('bodySize', 0),
                    'content_type': response.get('content', {}).get('mimeType', ''),
                    'type': 'video_file'
                })
            
            # Check for streaming manifests
            if any(ext in url.lower() for ext in ['.m3u8', '.mpd']):
                is_video_related = True
                video_analysis['manifest_urls'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'type': 'manifest'
                })
            
            # Check for video segments
            if any(ext in url.lower() for ext in ['.ts', '.m4s']):
                is_video_related = True
                video_analysis['video_segments'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'size': response.get('bodySize', 0),
                    'type': 'segment'
                })
            
            # Check for streaming URLs in manifest patterns
            if any(pattern in url.lower() for pattern in manifest_patterns):
                if any(ext in url.lower() for ext in streaming_formats):
                    is_video_related = True
                    video_analysis['streaming_urls'].append({
                        'url': url,
                        'method': request.get('method', ''),
                        'status': response.get('status', 0),
                        'type': 'streaming'
                    })
            
            # Check content type for video
            content_type = response.get('content', {}).get('mimeType', '')
            if content_type and ('video' in content_type or 'application/x-mpegURL' in content_type or 'application/dash+xml' in content_type):
                is_video_related = True
                if url not in [req['url'] for req in video_analysis['video_requests']]:
                    video_analysis['video_requests'].append({
                        'url': url,
                        'method': request.get('method', ''),
                        'status': response.get('status', 0),
                        'size': response.get('bodySize', 0),
                        'content_type': content_type,
                        'type': 'video_content'
                    })
            
            # Check for ad-related requests
            if any(ad_pattern in url.lower() for ad_pattern in ['ads', 'advertising', 'doubleclick', 'googlesyndication', 'adserver']):
                video_analysis['ad_requests'].append({
                    'url': url,
                    'method': request.get('method', ''),
                    'status': response.get('status', 0),
                    'type': 'ad'
                })
            
            if is_video_related:
                video_analysis['video_related_count'] += 1
        
        return video_analysis
        
    except Exception as e:
        print(f"Error analyzing HAR file {har_path}: {e}")
        return {
            'error': str(e),
            'video_requests': [],
            'streaming_urls': [],
            'manifest_urls': [],
            'video_segments': [],
            'ad_requests': [],
            'total_requests': 0,
            'video_related_count': 0
        }


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
    
    # Test HAR analysis on existing files
    await test_har_analysis()


if __name__ == "__main__":
    asyncio.run(main()) 