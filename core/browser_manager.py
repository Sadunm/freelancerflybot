#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Browser Manager Module
---------------------
Manages browser instances with anti-detection measures to avoid bot detection.
"""

import os
import json
import random
import logging
import tempfile
import platform
import subprocess
from typing import Dict, Any, Optional, List

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from freelancerfly_bot.utils.stealth import apply_stealth_settings
from freelancerfly_bot.utils.user_agents import get_random_user_agent
from freelancerfly_bot.utils.fingerprint import generate_fingerprint_overrides

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser instances with anti-detection measures."""
    
    def __init__(self, proxy: Optional[str] = None, headless: bool = True, 
                 session_id: Optional[str] = None, user_profile: Optional[str] = None):
        """
        Initialize browser manager.
        """
        self.proxy = proxy
        self.headless = headless
        self.session_id = session_id
        self.user_profile = user_profile
        self.driver = None
        self.profile_dir = None
        
        # Create profile directory if user_profile is specified
        if user_profile:
            self.profile_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "profiles",
                user_profile
            )
            os.makedirs(self.profile_dir, exist_ok=True)
    
    def get_driver(self):
        """
        Get a WebDriver instance with anti-detection measures.
        """
        if self.driver:
            return self.driver
        
        # Create Firefox options
        options = FirefoxOptions()
        
        # Set up Firefox profile
        if self.profile_dir:
            firefox_profile = FirefoxProfile(self.profile_dir)
        else:
            firefox_profile = FirefoxProfile()
        
        # Apply anti-detection settings
        self._configure_profile(firefox_profile)
        
        # Set headless mode
        if self.headless:
            options.add_argument("--headless")
        
        # Set proxy if provided
        if self.proxy:
            self._configure_proxy(firefox_profile)
        
        # Set Firefox preferences
        options.profile = firefox_profile
        
        # Set capabilities for console logs through options
        options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})
        
        # Create Firefox service
        service = FirefoxService(executable_path=self._get_geckodriver_path())
        
        # Create driver
        self.driver = webdriver.Firefox(
            service=service,
            options=options
        )
        
        # Random window size
        sizes = [
            (1366, 768), (1440, 900), (1536, 864), (1920, 1080), (1600, 900), (1280, 720)
        ]
        width, height = random.choice(sizes)
        self.driver.set_window_size(width, height)
        
        # Apply additional stealth settings via JavaScript
        apply_stealth_settings(self.driver)
        
        # Execute the fingerprint overrides JavaScript
        try:
            fingerprint_js = generate_fingerprint_overrides()
            self.driver.execute_script(fingerprint_js)
            logger.debug("Applied fingerprint overrides")
        except Exception as e:
            logger.error(f"Error applying fingerprint overrides: {str(e)}")
        
        # Hardware concurrency spoof
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    value: Math.floor(Math.random() * 6) + 2,
                    configurable: false,
                    enumerable: true
                });
            """)
        except Exception as e:
            logger.error(f"Error spoofing hardwareConcurrency: {str(e)}")
        
        logger.info("Created new Firefox WebDriver instance with anti-detection measures")
        return self.driver
    
    def _get_geckodriver_path(self) -> str:
        """
        Get path to geckodriver executable.
        """
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if platform.system() == "Windows":
            geckodriver = os.path.join(project_dir, "..", "geckodriver.exe")
        else:
            geckodriver = os.path.join(project_dir, "..", "geckodriver")
        
        if os.path.exists(geckodriver):
            return geckodriver
        
        if platform.system() == "Windows":
            return "geckodriver.exe"
        else:
            return "geckodriver"
    
    def _configure_profile(self, profile: FirefoxProfile):
        """
        Configure Firefox profile with anti-detection settings.
        """
        user_agent = get_random_user_agent()
        # Basic privacy settings
        profile.set_preference("privacy.trackingprotection.enabled", False)
        profile.set_preference("privacy.trackingprotection.pbm.enabled", False)
        profile.set_preference("privacy.trackingprotection.cryptomining.enabled", False)
        profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", False)
        # Disable WebRTC
        profile.set_preference("media.peerconnection.enabled", False)
        # Disable WebGL
        profile.set_preference("webgl.disabled", True)
        # Disable cache
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        # Disable browser auto-updates
        profile.set_preference("app.update.auto", False)
        profile.set_preference("app.update.enabled", False)
        # Disable telemetry
        profile.set_preference("toolkit.telemetry.enabled", False)
        profile.set_preference("toolkit.telemetry.unified", False)
        profile.set_preference("toolkit.telemetry.archive.enabled", False)
        # Set user agent
        profile.set_preference("general.useragent.override", user_agent)
        # Disable webdriver flag
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        # Random timezone (this is for extra randomization - not all browsers respect this, but it's worth adding)
        timezones = [
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Singapore", "Australia/Sydney"
        ]
        profile.set_preference("timezone", random.choice(timezones))
        # Internationalization
        profile.set_preference("intl.accept_languages", "en-US, en")
        profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision.microseconds", random.randint(2000, 20000))
        profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision", True)
        logger.debug("Configured Firefox profile with anti-detection settings")
    
    def _configure_proxy(self, profile: FirefoxProfile):
        """
        Configure proxy settings.
        """
        try:
            parts = self.proxy.split(':')
            if len(parts) == 2:
                ip, port = parts
                username, password = None, None
            elif len(parts) == 4:
                ip, port, username, password = parts
            else:
                raise ValueError(f"Invalid proxy format: {self.proxy}")
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", int(port))
            profile.set_preference("network.proxy.ssl", ip)
            profile.set_preference("network.proxy.ssl_port", int(port))
            profile.set_preference("network.proxy.ftp", ip)
            profile.set_preference("network.proxy.ftp_port", int(port))
            profile.set_preference("network.proxy.socks", ip)
            profile.set_preference("network.proxy.socks_port", int(port))
            profile.set_preference("network.proxy.no_proxies_on", "localhost,127.0.0.1")
            if username and password:
                profile.set_preference("network.proxy.socks_username", username)
                profile.set_preference("network.proxy.socks_password", password)
            logger.info(f"Configured proxy: {ip}:{port}")
        except Exception as e:
            logger.error(f"Error configuring proxy: {str(e)}")
    
    def quit(self):
        """Quit the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Quit WebDriver instance")
                # Cross-platform process cleanup
                if platform.system() == "Windows":
                    os.system("taskkill /f /im geckodriver.exe /t")
                else:
                    os.system("pkill -f geckodriver")
            except Exception as e:
                logger.error(f"Error quitting WebDriver: {str(e)}")
            finally:
                self.driver = None
