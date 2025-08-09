#!/usr/bin/env python3
"""
Demo script for the Intelligent Site Explorer

This script demonstrates how to use the site explorer to analyze websites
and collect HAR files for further analysis.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src import IntelligentSiteExplorer, load_config
from src.config.site_explorer_config import SiteExplorerConfig


async def demo_single_site():
    """Demonstrate exploring a single site."""
    print("🌐 Single Site Exploration Demo")
    print("=" * 50)
    
    # Create a basic configuration
    config = SiteExplorerConfig(
        headless=False,  # Show browser for demo
        timeout=30,
        max_scroll_attempts=3,
        video_detection_timeout=10
    )
    
    # Initialize the explorer
    explorer = IntelligentSiteExplorer(config)
    
    try:
        # Start the browser
        await explorer.start()
        
        # Explore a test site
        test_url = "https://httpbin.org/html"
        print(f"Exploring: {test_url}")
        
        result = await explorer.explore_site(test_url)
        
        if result.success:
            print(f"✅ Successfully explored {test_url}")
            print(f"   - HAR file: {result.har_file}")
            print(f"   - Video found: {result.video_found}")
            print(f"   - Obstacles handled: {result.obstacles_handled}")
        else:
            print(f"❌ Failed to explore {test_url}: {result.error}")
            
    except Exception as e:
        print(f"❌ Error during exploration: {e}")
    finally:
        await explorer.stop()


async def demo_test_sites():
    """Demonstrate exploring multiple test sites."""
    print("\n🧪 Test Sites Exploration Demo")
    print("=" * 50)
    
    # Load test sites
    test_sites_path = Path(__file__).parent.parent.parent / "data" / "test_sites.json"
    
    if not test_sites_path.exists():
        print("❌ Test sites file not found. Run 'site-explorer create-config' first.")
        return
    
    with open(test_sites_path, 'r') as f:
        test_data = json.load(f)
    
    # Take first 2 sites for demo
    demo_sites = test_data['test_sites'][:2]
    
    config = SiteExplorerConfig(
        headless=True,  # Headless for batch processing
        timeout=20,
        max_scroll_attempts=2
    )
    
    explorer = IntelligentSiteExplorer(config)
    
    try:
        await explorer.start()
        
        print(f"Exploring {len(demo_sites)} test sites...")
        
        results = await explorer.explore_multiple_sites(
            [site['url'] for site in demo_sites]
        )
        
        print(f"\nResults:")
        for i, result in enumerate(results):
            site_name = demo_sites[i]['name']
            if result.success:
                print(f"  ✅ {site_name}: Success")
                print(f"     HAR: {result.har_file}")
            else:
                print(f"  ❌ {site_name}: {result.error}")
        
        # Print statistics
        explorer.print_stats()
        
    except Exception as e:
        print(f"❌ Error during batch exploration: {e}")
    finally:
        await explorer.stop()


async def demo_configuration():
    """Demonstrate configuration management."""
    print("\n⚙️ Configuration Management Demo")
    print("=" * 50)
    
    # Create a custom configuration
    custom_config = SiteExplorerConfig(
        headless=True,
        timeout=45,
        max_scroll_attempts=5,
        cookie_consent_selectors=[
            "button[data-testid='cookie-accept']",
            ".cookie-banner .accept",
            "#cookie-accept"
        ],
        ad_handling_wait_time=8,
        video_detection_timeout=15
    )
    
    # Save configuration
    config_path = Path("custom_explorer_config.yaml")
    save_config(custom_config, config_path)
    print(f"✅ Saved custom configuration to: {config_path}")
    
    # Load configuration
    loaded_config = load_config(config_path)
    print(f"✅ Loaded configuration: {loaded_config}")
    
    # Clean up
    config_path.unlink()
    print(f"🧹 Cleaned up temporary config file")


def main():
    """Run all demos."""
    print("🚀 Intelligent Site Explorer Demo Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Please run this script from the project root directory")
        return
    
    # Run demos
    asyncio.run(demo_single_site())
    asyncio.run(demo_test_sites())
    asyncio.run(demo_configuration())
    
    print("\n🎉 Demo suite completed!")
    print("\nNext steps:")
    print("1. Try the CLI: python -m src.site_explorer_cli explore <url>")
    print("2. Check the generated HAR files")
    print("3. Use the LangChain integration for analysis")


if __name__ == "__main__":
    main() 