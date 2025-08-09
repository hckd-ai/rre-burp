"""
Cookie Consent Handler

Intelligent cookie consent dialog detection and handling using Playwright.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .models import CookieConsentConfig, ConsentButton, ConsentButtonType, ConsentDialogType

logger = logging.getLogger(__name__)

class CookieConsentHandler:
    """Handles cookie consent dialogs intelligently."""
    
    def __init__(self, config: Optional[CookieConsentConfig] = None):
        self.config = config or CookieConsentConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Define common consent button patterns
        self.consent_buttons = self._build_consent_button_patterns()
        
        # Define common dialog selectors
        self.dialog_selectors = self._build_dialog_selectors()
    
    def _build_consent_button_patterns(self) -> List[ConsentButton]:
        """Build patterns for common consent buttons."""
        return [
            # High priority - direct text matches
            ConsentButton("Accept All", ConsentButtonType.ACCEPT_ALL, 'button:has-text("Accept All")', priority=1),
            ConsentButton("Accept", ConsentButtonType.ACCEPT, 'button:has-text("Accept")', priority=1),
            ConsentButton("Allow All", ConsentButtonType.ACCEPT_ALL, 'button:has-text("Allow All")', priority=1),
            ConsentButton("Allow", ConsentButtonType.ALLOW, 'button:has-text("Allow")', priority=1),
            ConsentButton("OK", ConsentButtonType.OK, 'button:has-text("OK")', priority=1),
            ConsentButton("Got it", ConsentButtonType.GOT_IT, 'button:has-text("Got it")', priority=1),
            ConsentButton("Understood", ConsentButtonType.UNDERSTOOD, 'button:has-text("Understood")', priority=1),
            ConsentButton("Proceed", ConsentButtonType.PROCEED, 'button:has-text("Proceed")', priority=1),
            ConsentButton("Continue", ConsentButtonType.CONTINUE, 'button:has-text("Continue")', priority=1),
            
            # Medium priority - attribute-based selectors
            ConsentButton("Accept Button", ConsentButtonType.ACCEPT, '[id*="accept"]', priority=2),
            ConsentButton("Accept Button", ConsentButtonType.ACCEPT, '[class*="accept"]', priority=2),
            ConsentButton("Allow Button", ConsentButtonType.ALLOW, '[id*="allow"]', priority=2),
            ConsentButton("Allow Button", ConsentButtonType.ALLOW, '[class*="allow"]', priority=2),
            
            # Lower priority - generic patterns
            ConsentButton("Cookie Button", ConsentButtonType.ACCEPT, '[id*="cookie"] button', priority=3),
            ConsentButton("Cookie Button", ConsentButtonType.ACCEPT, '[class*="cookie"] button', priority=3),
            ConsentButton("Consent Button", ConsentButtonType.ACCEPT, '[id*="consent"] button', priority=3),
            ConsentButton("Consent Button", ConsentButtonType.ACCEPT, '[class*="consent"] button', priority=3),
            ConsentButton("GDPR Button", ConsentButtonType.ACCEPT, '[id*="gdpr"] button', priority=3),
            ConsentButton("GDPR Button", ConsentButtonType.ACCEPT, '[class*="gdpr"] button', priority=3),
        ]
    
    def _build_dialog_selectors(self) -> List[str]:
        """Build selectors for common consent dialog containers."""
        return [
            # Cookie consent specific
            '[id*="cookie"]',
            '[class*="cookie"]',
            '[id*="consent"]',
            '[class*="consent"]',
            '[id*="gdpr"]',
            '[class*="gdpr"]',
            '[id*="privacy"]',
            '[class*="privacy"]',
            
            # Generic popup/modal selectors
            '[role="dialog"]',
            '[class*="modal"]',
            '[class*="popup"]',
            '[class*="overlay"]',
            '[class*="banner"]',
            '[class*="notification"]',
            
            # Common consent frameworks
            '[id*="onetrust"]',
            '[class*="onetrust"]',
            '[id*="cookiebot"]',
            '[class*="cookiebot"]',
            '[id*="gdpr-cookie"]',
            '[class*="gdpr-cookie"]',
        ]
    
    async def handle_consent(self, page: Page, url: str) -> bool:
        """
        Handle cookie consent on the given page.
        
        Args:
            page: Playwright page object
            url: Current page URL
            
        Returns:
            bool: True if consent was handled, False otherwise
        """
        if not self.config.enabled:
            return False
            
        # Check if we should skip this site
        if self._should_skip_site(url):
            self.logger.info(f"Skipping consent handling for {url}")
            return False
            
        try:
            self.logger.info(f"Handling cookie consent for {url}")
            
            # Try to find and handle consent dialogs
            consent_handled = await self._handle_consent_dialogs(page)
            
            if consent_handled:
                self.logger.info(f"Successfully handled consent for {url}")
                return True
            else:
                self.logger.info(f"No consent dialog found for {url}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error handling consent for {url}: {e}")
            return False
    
    def _should_skip_site(self, url: str) -> bool:
        """Check if consent handling should be skipped for this site."""
        for skip_site in self.config.skip_sites:
            if skip_site.lower() in url.lower():
                return True
        return False
    
    async def _handle_consent_dialogs(self, page: Page) -> bool:
        """Find and handle consent dialogs."""
        try:
            # First, try to find existing consent dialogs with minimal wait
            dialog_found = await self._find_consent_dialog(page)
            
            if dialog_found:
                return await self._click_consent_button(page)
            
            # If no dialog found, don't wait - just return False
            return False
            
        except Exception as e:
            self.logger.error(f"Error in consent dialog handling: {e}")
            return False
    
    async def _find_consent_dialog(self, page: Page) -> bool:
        """Find if a consent dialog is present on the page."""
        try:
            for selector in self.dialog_selectors:
                try:
                    # Use very short timeout to avoid blocking
                    element = await page.wait_for_selector(selector, timeout=500)  # Reduced to 500ms
                    if element and await element.is_visible():
                        self.logger.debug(f"Found consent dialog with selector: {selector}")
                        return True
                except PlaywrightTimeoutError:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Error finding consent dialog: {e}")
            return False
    
    async def _click_consent_button(self, page: Page) -> bool:
        """Click the appropriate consent button."""
        try:
            # Sort buttons by priority
            sorted_buttons = sorted(self.consent_buttons, key=lambda x: x.priority)
            
            for button in sorted_buttons:
                try:
                    if await self._try_click_button(page, button):
                        return True
                except Exception as e:
                    self.logger.debug(f"Failed to click button {button.text}: {e}")
                    continue
            
            # Try custom selectors if provided
            if self.config.custom_selectors:
                for selector in self.config.custom_selectors:
                    try:
                        if await self._try_click_selector(page, selector):
                            return True
                    except Exception as e:
                        self.logger.debug(f"Failed to click custom selector {selector}: {e}")
                        continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error clicking consent button: {e}")
            return False
    
    async def _try_click_button(self, page: Page, button: ConsentButton) -> bool:
        """Try to click a specific consent button."""
        try:
            # Wait for button with configured timeout
            element = await page.wait_for_selector(button.selector, timeout=self.config.timeout)
            
            if element:
                # Check if element is visible (unless in aggressive mode)
                if not self.config.aggressive_mode and not await element.is_visible():
                    return False
                
                # Click the button
                await element.click()
                self.logger.info(f"Clicked consent button: {button.text}")
                
                # Wait after clicking
                await asyncio.sleep(self.config.wait_after_click)
                
                return True
                
        except PlaywrightTimeoutError:
            return False
        except Exception as e:
            self.logger.debug(f"Error clicking button {button.text}: {e}")
            return False
        
        return False
    
    async def _try_click_selector(self, page: Page, selector: str) -> bool:
        """Try to click a custom selector."""
        try:
            element = await page.wait_for_selector(selector, timeout=self.config.timeout)
            
            if element:
                if not self.config.aggressive_mode and not await element.is_visible():
                    return False
                
                await element.click()
                self.logger.info(f"Clicked custom selector: {selector}")
                
                await asyncio.sleep(self.config.wait_after_click)
                return True
                
        except PlaywrightTimeoutError:
            return False
        except Exception as e:
            self.logger.debug(f"Error clicking custom selector {selector}: {e}")
            return False
        
        return False
    
    async def wait_for_consent_removal(self, page: Page, timeout: int = 5000) -> bool:
        """Wait for consent dialog to disappear after handling."""
        try:
            # Wait for any consent dialog to disappear
            for selector in self.dialog_selectors:
                try:
                    await page.wait_for_selector(selector, state='hidden', timeout=timeout)
                    return True
                except PlaywrightTimeoutError:
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for consent removal: {e}")
            return False 