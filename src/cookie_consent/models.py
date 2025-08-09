"""
Cookie Consent Models

Data models for cookie consent configuration and consent button types.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class ConsentButtonType(Enum):
    """Types of consent buttons."""
    ACCEPT = "accept"
    ACCEPT_ALL = "accept_all"
    ALLOW = "allow"
    OK = "ok"
    CONTINUE = "continue"
    GOT_IT = "got_it"
    UNDERSTOOD = "understood"
    PROCEED = "proceed"

class ConsentDialogType(Enum):
    """Types of consent dialogs."""
    COOKIE = "cookie"
    GDPR = "gdpr"
    PRIVACY = "privacy"
    TERMS = "terms"
    NOTIFICATION = "notification"
    POPUP = "popup"

@dataclass
class ConsentButton:
    """Represents a consent button with its properties."""
    text: str
    button_type: ConsentButtonType
    selector: str
    priority: int = 1  # Higher priority buttons are tried first
    attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class CookieConsentConfig:
    """Configuration for cookie consent handling."""
    enabled: bool = True
    timeout: int = 3000  # 3 seconds timeout
    max_attempts: int = 3
    wait_after_click: float = 0.5  # seconds to wait after clicking
    aggressive_mode: bool = False  # Skip waiting for elements to be visible
    custom_selectors: List[str] = field(default_factory=list)
    skip_sites: List[str] = field(default_factory=list)
    log_level: str = "INFO" 