#!/usr/bin/env python3
"""
Test script for the Video Discovery API.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_api():
    """Test the video discovery API endpoints."""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Video Discovery API...")
        print("=" * 50)
        
        # Test health check
        print("\n1. Testing health check...")
        try:
            async with session.get(f"{base_url}/api/v1/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/api/v1/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Root endpoint: {data}")
                else:
                    print(f"❌ Root endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test video discovery with POST
        print("\n3. Testing video discovery (POST)...")
        try:
            payload = {
                "url": "https://tubitv.com/",
                "max_videos": 5,
                "timeout": 15,
                "headless": True
            }
            
            async with session.post(
                f"{base_url}/api/v1/discover",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Video discovery successful!")
                    print(f"   Found {data['total_videos']} videos")
                    print(f"   Time taken: {data['exploration_time']:.2f}s")
                    
                    # Show first few videos
                    for i, video in enumerate(data['videos_found'][:3], 1):
                        print(f"   Video {i}: {video['title']} ({video['video_type']})")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Video discovery failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Video discovery error: {e}")
        
        # Test video discovery with GET
        print("\n4. Testing video discovery (GET)...")
        try:
            params = {
                "max_videos": 3,
                "timeout": 10,
                "headless": True
            }
            
            # URL encode the Tubi TV URL
            encoded_url = "https%3A//tubitv.com/"
            
            async with session.get(
                f"{base_url}/api/v1/discover/{encoded_url}",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GET video discovery successful!")
                    print(f"   Found {data['total_videos']} videos")
                    print(f"   Time taken: {data['exploration_time']:.2f}s")
                    
                    # Show first few videos
                    for i, video in enumerate(data['videos_found'][:2], 1):
                        print(f"   Video {i}: {video['title']} ({video['video_type']})")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ GET video discovery failed: {response.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ GET video discovery error: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api()) 