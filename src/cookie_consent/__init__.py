"""
Cookie Consent Handler Package

A dedicated package for handling cookie consent dialogs and popups
across different websites with intelligent detection and handling.
"""

from .cookie_handler import CookieConsentHandler
from .models import CookieConsentConfig, ConsentButton

__all__ = ["CookieConsentHandler", "CookieConsentConfig", "ConsentButton"] 