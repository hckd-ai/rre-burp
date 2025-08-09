"""
RRE Burp - Request Response Explorer with AI Integration

A comprehensive toolkit for analyzing web traffic using RRE components
integrated with LangChain for intelligent analysis.
"""

# Core RRE components
from .rre_core import (
    EnhancedRREAnalyzer,
    IntelligentHARAnalyzer,
    collect_har
)

# LangChain integration
from .langchain_integration import (
    HARCollectorTool,
    RREAnalysisTool,
    TrafficIntelligenceChain,
    AutomatedExploitChain,
    TrafficQueryChain,
    ConfigManager
)

# Site Explorer
from .site_explorer import IntelligentSiteExplorer

# Configuration
from .config.site_explorer_config import (
    SiteExplorerConfig,
    load_config,
    save_config
)

# Utilities
from .utils.web_helpers import (
    wait_for_page_stable,
    detect_video_content,
    handle_cookie_consent,
    handle_ads_and_overlays
)

__version__ = "1.0.0"

__all__ = [
    # Core RRE
    'EnhancedRREAnalyzer',
    'IntelligentHARAnalyzer',
    'collect_har',
    
    # LangChain Integration
    'HARCollectorTool',
    'RREAnalysisTool',
    'TrafficIntelligenceChain',
    'AutomatedExploitChain',
    'TrafficQueryChain',
    'ConfigManager',
    
    # Site Explorer
    'IntelligentSiteExplorer',
    
    # Configuration
    'SiteExplorerConfig',
    'load_config',
    'save_config',
    
    # Utilities
    'wait_for_page_stable',
    'detect_video_content',
    'handle_cookie_consent',
    'handle_ads_and_overlays'
] 