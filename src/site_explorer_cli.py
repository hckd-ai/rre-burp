#!/usr/bin/env python3
"""
Site Explorer CLI
=================

Command-line interface for the intelligent site explorer.
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.site_explorer.intelligent_explorer import IntelligentSiteExplorer
from src.config.site_explorer_config import load_config, save_config


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('site_explorer.log')
        ]
    )


async def explore_single_site(url: str, site_name: str = None, config_path: str = None, verbose: bool = False):
    """Explore a single site"""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        async with IntelligentSiteExplorer(config_path=config_path) as explorer:
            logger.info(f"Starting exploration of {url}")
            result = await explorer.explore_site(url, site_name)
            
            # Print results
            print(f"\n{'='*60}")
            print(f"EXPLORATION RESULTS: {result['site_name']}")
            print(f"{'='*60}")
            print(f"URL: {result['url']}")
            print(f"Success: {'✅' if result['success'] else '❌'}")
            print(f"Video Found: {'✅' if result['video_found'] else '❌'}")
            print(f"HAR Collected: {'✅' if result['har_collected'] else '❌'}")
            print(f"Exploration Time: {result['exploration_time']:.2f}s")
            
            if result['video_info']:
                print(f"\nVideo Information:")
                for key, value in result['video_info'].items():
                    print(f"  {key}: {value}")
            
            if result['har_path']:
                print(f"\nHAR File: {result['har_path']}")
            
            if result['errors']:
                print(f"\nErrors:")
                for error in result['errors']:
                    print(f"  ❌ {error}")
            
            explorer.print_stats()
            
            return result
            
    except Exception as e:
        logger.error(f"Exploration failed: {e}")
        print(f"❌ Exploration failed: {e}")
        return None


async def explore_test_sites(config_path: str = None, verbose: bool = False, limit: int = None):
    """Explore test sites from test_sites.json"""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    # Load test sites
    test_sites_path = Path("test_sites.json")
    if not test_sites_path.exists():
        print("❌ test_sites.json not found. Please run the script from the project root.")
        return None
    
    with open(test_sites_path, 'r') as f:
        test_data = json.load(f)
    
    sites = test_data['test_sites']
    if limit:
        sites = sites[:limit]
    
    urls = [site['url'] for site in sites]
    site_names = [site['name'] for site in sites]
    
    print(f"🚀 Starting exploration of {len(sites)} test sites...")
    
    try:
        async with IntelligentSiteExplorer(config_path=config_path) as explorer:
            results = await explorer.explore_multiple_sites(urls, site_names)
            
            # Print summary
            print(f"\n{'='*60}")
            print("EXPLORATION SUMMARY")
            print(f"{'='*60}")
            
            successful = sum(1 for r in results if r['success'])
            videos_found = sum(1 for r in results if r['video_found'])
            hars_collected = sum(1 for r in results if r['har_collected'])
            
            print(f"Total Sites: {len(results)}")
            print(f"Successful: {successful}")
            print(f"Videos Found: {videos_found}")
            print(f"HARs Collected: {hars_collected}")
            
            # Print detailed results
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['site_name']}")
                print(f"   URL: {result['url']}")
                print(f"   Status: {'✅' if result['success'] else '❌'}")
                print(f"   Video: {'✅' if result['video_found'] else '❌'}")
                print(f"   HAR: {'✅' if result['har_collected'] else '❌'}")
                
                if result['har_path']:
                    print(f"   HAR File: {result['har_path']}")
                
                if result['errors']:
                    print(f"   Errors: {len(result['errors'])}")
            
            explorer.print_stats()
            return results
            
    except Exception as e:
        logger.error(f"Test exploration failed: {e}")
        print(f"❌ Test exploration failed: {e}")
        return None


async def create_config(config_path: str = "site_explorer_config.yaml"):
    """Create a default configuration file"""
    from src.config.site_explorer_config import SiteExplorerConfig, save_config
    
    config = SiteExplorerConfig()
    save_config(config, config_path)
    print(f"✅ Configuration file created: {config_path}")
    print("You can now edit this file to customize the explorer behavior.")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Intelligent Site Explorer - Find videos and collect HAR files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explore a single site
  python site_explorer_cli.py https://example.com "Example Site"
  
  # Explore test sites
  python site_explorer_cli.py --test
  
  # Explore with custom config
  python site_explorer_cli.py --test --config my_config.yaml
  
  # Create default config
  python site_explorer_cli.py --create-config
  
  # Verbose output
  python site_explorer_cli.py --test --verbose
        """
    )
    
    parser.add_argument("url", nargs="?", help="URL to explore")
    parser.add_argument("site_name", nargs="?", help="Name for the site")
    
    parser.add_argument("--test", action="store_true", help="Explore test sites from test_sites.json")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--limit", type=int, help="Limit number of test sites to explore")
    
    args = parser.parse_args()
    
    if args.create_config:
        asyncio.run(create_config(args.config or "site_explorer_config.yaml"))
        return
    
    if args.test:
        asyncio.run(explore_test_sites(args.config, args.verbose, args.limit))
    elif args.url:
        asyncio.run(explore_single_site(args.url, args.site_name, args.config, args.verbose))
    else:
        parser.print_help()
        print("\n❌ Please provide a URL or use --test to explore test sites.")


if __name__ == "__main__":
    main() 