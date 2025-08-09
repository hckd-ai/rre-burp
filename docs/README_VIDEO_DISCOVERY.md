# Video Discovery Service

A focused service for discovering video URLs from web pages using Playwright automation.

## Overview

The Video Discovery Service is designed to:
- **Find video URLs** from any web page
- **Detect multiple video types**: native HTML5, embedded (YouTube, Vimeo, etc.), custom players
- **Navigate intelligently**: automatically explore video sections and click thumbnails
- **Provide clean API**: simple REST endpoints for integration
- **Handle common obstacles**: cookie consent, ads, overlays

## Architecture

```
src/
├── video_discovery/           # Core video discovery logic
│   ├── __init__.py
│   ├── models.py             # Data models and enums
│   └── video_discoverer.py   # Main discovery class
├── api/                      # FastAPI server
│   ├── __init__.py
│   ├── server.py             # FastAPI app configuration
│   └── routes.py             # API endpoints
├── video_discovery_cli.py    # CLI for testing
└── run_api_server.py         # Server runner
```

## Features

### Video Detection
- **Native HTML5**: `<video>` elements with direct URLs
- **Embedded**: YouTube, Vimeo, Dailymotion, Twitch iframes
- **Custom Players**: JavaScript-based video players
- **Streaming**: HLS (.m3u8) and DASH (.mpd) manifests

### Intelligent Navigation
- **Cookie Consent**: Automatically handle GDPR/cookie dialogs
- **Ad Handling**: Close overlays and popups
- **Content Loading**: Smart scrolling to trigger lazy loading
- **Section Navigation**: Find and explore video-specific areas
- **Thumbnail Interaction**: Click previews to trigger video content

### API Endpoints

#### POST `/api/v1/discover`
Discover videos from a URL synchronously.

**Request:**
```json
{
  "url": "https://example.com",
  "max_videos": 10,
  "timeout": 60
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "videos_found": [
    {
      "title": "Sample Video",
      "video_url": "https://example.com/video.mp4",
      "video_type": "native",
      "source": "native",
      "player_url": null,
      "thumbnail_url": null,
      "duration": null,
      "description": null
    }
  ],
  "total_videos": 1,
  "exploration_time": 5.23,
  "error_message": null
}
```

#### POST `/api/v1/discover/async`
Start video discovery as a background task.

#### GET `/api/v1/status/{task_id}`
Check status of background discovery tasks.

#### GET `/api/v1/health`
Health check endpoint.

## Quick Start

### 1. Install Dependencies
```bash
# Install API dependencies
pip install -r requirements_api.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Run the API Server
```bash
cd src
python run_api_server.py
```

The server will start at `http://localhost:8000`

### 3. Test Video Discovery
```bash
# Using the CLI
cd src
python video_discovery_cli.py "https://www.youtube.com"

# Using the test script
python test_video_discovery.py
```

### 4. API Usage Examples

#### Python Client
```python
import requests

# Discover videos
response = requests.post("http://localhost:8000/api/v1/discover", json={
    "url": "https://www.youtube.com",
    "max_videos": 5
})

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['total_videos']} videos")
    for video in result['videos_found']:
        print(f"- {video['title']}: {video['video_url']}")
```

#### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/discover" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com", "max_videos": 5}'
```

## Configuration

The service uses configuration classes from `site_explorer_config.py`:

- **VideoDetectionConfig**: Video selectors and detection settings
- **CookieConsentConfig**: Cookie handling preferences
- **AdHandlingConfig**: Ad and overlay handling settings

## Video Types

### Native HTML5
- Direct video files (.mp4, .webm, .ogg)
- HTML5 `<video>` elements
- Source URLs in video attributes

### Embedded
- **YouTube**: youtube.com, youtu.be
- **Vimeo**: vimeo.com
- **Dailymotion**: dailymotion.com
- **Twitch**: twitch.tv

### Custom Players
- JavaScript-based video players
- Custom video containers
- Data attributes with video URLs

### Streaming
- HLS manifests (.m3u8)
- DASH manifests (.mpd)
- Video segments (.ts, .m4s)

## Error Handling

The service gracefully handles:
- Network timeouts
- Page load failures
- Element interaction errors
- Cookie consent issues
- Ad overlays

All errors are logged and returned in the API response.

## Performance

- **Typical discovery time**: 5-30 seconds per URL
- **Browser automation**: Headless Chromium for speed
- **Parallel processing**: Can handle multiple requests
- **Background tasks**: Async endpoint for long-running discoveries

## Security Considerations

- **Headless browser**: No visual access to user data
- **Timeout limits**: Prevents infinite loops
- **Element limits**: Caps on number of elements processed
- **Error isolation**: Failures don't affect other requests

## Future Enhancements

- **Video quality detection**: Resolution, bitrate analysis
- **Content filtering**: Age restrictions, region blocking
- **Batch processing**: Multiple URLs in single request
- **Caching**: Store results for repeated URLs
- **Analytics**: Discovery success rates and patterns

## Troubleshooting

### Common Issues

1. **No videos found**
   - Check if the site requires JavaScript
   - Verify the URL is accessible
   - Try increasing timeout values

2. **Browser crashes**
   - Ensure Playwright is properly installed
   - Check system memory availability
   - Update Playwright to latest version

3. **Slow performance**
   - Reduce max_videos parameter
   - Use async endpoint for long-running tasks
   - Check network connectivity

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details. 