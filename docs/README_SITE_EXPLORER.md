# Intelligent Site Explorer

An intelligent web crawler that can navigate websites, handle modern web challenges (cookie consent, ads, overlays), find video content, and collect HAR files for analysis.

## Features

### 🧠 Intelligent Navigation
- **Cookie Consent Handling**: Automatically detects and handles GDPR/cookie consent dialogs
- **Ad & Overlay Management**: Intelligently skips or closes advertisements and popups
- **Dynamic Content Loading**: Smart scrolling to load lazy-loaded content
- **Page Stability Detection**: Waits for pages to become stable before proceeding

### 🎥 Video Detection
- **Multiple Video Types**: Native HTML5 video, embedded players (YouTube, Vimeo), custom players
- **Smart Playback**: Attempts to start video playback to capture streaming traffic
- **Duration Validation**: Filters out short videos to focus on meaningful content

### 📊 HAR Collection
- **Comprehensive Capture**: Records all network traffic, screenshots, and page snapshots
- **Organized Output**: Structured HAR files with descriptive naming
- **Batch Processing**: Can explore multiple sites in sequence

### ⚙️ Configurable Behavior
- **Flexible Settings**: Customizable timeouts, selectors, and behavior patterns
- **YAML Configuration**: Easy-to-edit configuration files
- **Environment Adaptation**: Different strategies for different types of sites

## Installation

### Prerequisites
- Python 3.10+
- Playwright browser binaries

### Setup
```bash
# Install dependencies
pip install -r requirements_langchain.txt

# Install Playwright browsers
playwright install chromium

# Create default configuration
python site_explorer_cli.py --create-config
```

## Quick Start

### Explore a Single Site
```bash
python site_explorer_cli.py "https://example.com" "Example Site"
```

### Explore Test Sites
```bash
# Explore all test sites
python site_explorer_cli.py --test

# Explore with limit
python site_explorer_cli.py --test --limit 3

# Verbose output
python site_explorer_cli.py --test --verbose
```

### Custom Configuration
```bash
# Use custom config file
python site_explorer_cli.py --test --config my_config.yaml
```

## Configuration

The site explorer uses a YAML configuration file (`site_explorer_config.yaml`) with the following structure:

```yaml
# Browser settings
headless: true
viewport_width: 1920
viewport_height: 1080
user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36..."

# Timing settings
page_load_timeout: 30.0
navigation_timeout: 20.0
wait_for_stable: 3.0
scroll_pause: 1.0

# Cookie consent handling
cookie_consent:
  selectors:
    - '[id*="cookie"]'
    - '[class*="consent"]'
    - 'div[role="dialog"]'
  button_texts:
    - "Accept"
    - "Accept All"
    - "Continue"
  wait_after_consent: 2.0

# Ad handling
ad_handling:
  ad_selectors:
    - '[id*="ad"]'
    - '[class*="banner"]'
    - 'iframe[src*="ads"]'
  skip_selectors:
    - '[id*="skip"]'
    - 'button:contains("Skip")'
  max_ad_wait: 30.0

# Video detection
video_detection:
  video_selectors:
    - 'video'
    - '[data-video]'
    - 'iframe[src*="youtube"]'
  player_selectors:
    - '[class*="player"]'
    - '[class*="video-player"]'
  play_selectors:
    - '[class*="play"]'
    - '[aria-label*="Play"]'
  video_load_wait: 5.0
  min_video_duration: 10.0

# HAR collection
har_output_dir: "collected_hars"
har_filename_template: "{site_name}_{timestamp}.har"
```

## Architecture

### Package Structure
```
src/
├── __init__.py                 # Main package exports
├── config/
│   ├── __init__.py            # Configuration exports
│   └── site_explorer_config.py # Configuration classes and management
├── site_explorer/
│   ├── __init__.py            # Site explorer exports
│   └── intelligent_explorer.py # Main explorer class
└── utils/
    ├── __init__.py            # Utility exports
    └── web_helpers.py         # Web interaction utilities
```

### Core Components

#### 1. IntelligentSiteExplorer
Main class that orchestrates the entire exploration process:
- Browser management and lifecycle
- Site navigation and interaction
- HAR collection and storage
- Statistics and reporting

#### 2. Web Helpers
Utility functions for common web tasks:
- `wait_for_page_stable()`: Ensures page is fully loaded
- `handle_cookie_consent()`: Manages consent dialogs
- `handle_ads_and_overlays()`: Deals with advertisements
- `detect_video_content()`: Finds video elements
- `scroll_page_intelligently()`: Loads dynamic content

#### 3. Configuration Management
Flexible configuration system:
- Default configurations for common scenarios
- YAML file support for customization
- Environment-specific settings

## Usage Examples

### Python API
```python
import asyncio
from src.site_explorer import IntelligentSiteExplorer

async def explore_sites():
    async with IntelligentSiteExplorer() as explorer:
        # Single site
        result = await explorer.explore_site(
            "https://example.com", 
            "Example Site"
        )
        
        # Multiple sites
        urls = ["https://site1.com", "https://site2.com"]
        results = await explorer.explore_multiple_sites(urls)
        
        # Print statistics
        explorer.print_stats()

# Run exploration
asyncio.run(explore_sites())
```

### Command Line
```bash
# Basic usage
python site_explorer_cli.py "https://example.com"

# Test mode with verbose logging
python site_explorer_cli.py --test --verbose

# Custom configuration
python site_explorer_cli.py --test --config production_config.yaml

# Limit test sites
python site_explorer_cli.py --test --limit 5
```

## Test Sites

The system includes a curated list of test sites in `test_sites.json`:

- **BookWyrm**: Federated social reading platform
- **Lemmy**: Federated link aggregator
- **Peertube**: Decentralized video sharing
- **Mastodon**: Decentralized social media
- **Matrix**: Communication protocol
- **Gitea**: Git hosting service
- **Nextcloud**: File sharing platform
- **Jitsi**: Video conferencing
- **Synapse**: Matrix server
- **Funkwhale**: Music streaming platform

These sites provide various complexity levels and video content types for testing.

## Output

### HAR Files
HAR files are saved in the configured output directory with descriptive names:
```
collected_hars/
├── bookwyrm_social_20241201_143022.har
├── lemmy_world_20241201_143156.har
└── peertube_social_20241201_143245.har
```

### Logs
Comprehensive logging is available:
- Console output for real-time monitoring
- File logging (`site_explorer.log`) for debugging
- Verbose mode for detailed analysis

### Statistics
The explorer provides detailed statistics:
```
==================================================
EXPLORATION STATISTICS
==================================================
Sites visited: 3
Videos found: 2
HAR files collected: 3
Errors encountered: 0
Total exploration time: 45.23s
==================================================
```

## Advanced Features

### Custom Selectors
Add site-specific selectors to your configuration:
```yaml
cookie_consent:
  selectors:
    - '.custom-cookie-banner'  # Site-specific selector
    - '#gdpr-notice'           # Another custom selector
```

### Behavior Customization
Tune the explorer for different site types:
```yaml
# For slow-loading sites
page_load_timeout: 60.0
wait_for_stable: 10.0

# For ad-heavy sites
ad_handling:
  max_ad_wait: 45.0
  wait_after_skip: 2.0
```

### Video Detection Tuning
Optimize for specific video types:
```yaml
video_detection:
  min_video_duration: 30.0  # Only longer videos
  video_load_wait: 10.0     # Longer wait for complex players
```

## Troubleshooting

### Common Issues

#### 1. Browser Launch Failures
```bash
# Reinstall Playwright browsers
playwright install chromium

# Check system dependencies
playwright install-deps
```

#### 2. Timeout Errors
- Increase timeouts in configuration
- Check network connectivity
- Verify site accessibility

#### 3. Video Detection Issues
- Review video selectors in configuration
- Check browser console for JavaScript errors
- Verify video elements are present in DOM

#### 4. HAR Collection Problems
- Ensure output directory is writable
- Check disk space availability
- Verify browser permissions

### Debug Mode
Enable verbose logging for detailed analysis:
```bash
python site_explorer_cli.py --test --verbose
```

### Configuration Validation
Validate your configuration file:
```python
from src.config import load_config

try:
    config = load_config("my_config.yaml")
    print("Configuration is valid")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Integration with RRE

The collected HAR files can be directly analyzed using the RRE (Request Response Explorer) system:

```python
from rre_enhanced import EnhancedRREAnalyzer

# Analyze collected HAR
analyzer = EnhancedRREAnalyzer("collected_hars/bookwyrm_social_20241201_143022.har")
analyzer.load_har_entries()
analyzer.analyze_patterns()
```

## Contributing

### Adding New Features
1. Extend the configuration classes in `src/config/`
2. Add new utility functions in `src/utils/`
3. Update the main explorer class in `src/site_explorer/`
4. Add tests and documentation

### Testing
```bash
# Test with a single site
python site_explorer_cli.py "https://httpbin.org" "Test Site"

# Test with known video sites
python site_explorer_cli.py "https://vimeo.com" "Vimeo"
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review configuration examples
3. Enable verbose logging for debugging
4. Check the log files for detailed error information 