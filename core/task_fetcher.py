#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Browser Manager Module
---------------------
Manages browser instances with anti-detection measures to avoid bot detection.
"""

import os
import random
import logging
import platform
from typing import Optional

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
        self.proxy = proxy
        self.headless = headless
        self.session_id = session_id
        self.user_profile = user_profile
        self.driver = None

        # User-specific Firefox profile directory
        if user_profile:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.profile_dir = os.path.join(project_root, "profiles", user_profile)
            os.makedirs(self.profile_dir, exist_ok=True)
        else:
            self.profile_dir = None

    def get_driver(self):
        """Get a WebDriver instance with anti-detection measures."""
        if self.driver:
            return self.driver

        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")

        # Use or create Firefox profile
        if self.profile_dir:
            firefox_profile = FirefoxProfile(self.profile_dir)
        else:
            firefox_profile = FirefoxProfile()

        self._configure_profile(firefox_profile)

        if self.proxy:
            self._configure_proxy(firefox_profile)

        options.profile = firefox_profile
        options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

        # Geckodriver path
        service = FirefoxService(executable_path=self._get_geckodriver_path())

        # Create the browser
        self.driver = webdriver.Firefox(service=service, options=options)

        # Set random window size
        for _ in range(3):
            try:
                width, height = random.choice([
                    (1366, 768), (1440, 900), (1536, 864), (1920, 1080), (1600, 900), (1280, 720)
                ])
                self.driver.set_window_size(width, height)
                break
            except Exception:
                continue

        # Stealth and fingerprint
        try:
            apply_stealth_settings(self.driver)
        except Exception as e:
            logger.error(f"Stealth JS inject failed: {str(e)}")
        try:
            fingerprint_js = generate_fingerprint_overrides()
            self.driver.execute_script(fingerprint_js)
        except Exception as e:
            logger.error(f"Fingerprint spoof failed: {str(e)}")
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    value: Math.floor(Math.random() * 6) + 2,
                    configurable: false,
                    enumerable: true
                });
            """)
        except Exception as e:
            logger.error(f"HardwareConcurrency spoof failed: {str(e)}")

        logger.info("Created new Firefox WebDriver with anti-detection.")
        return self.driver

    def _get_geckodriver_path(self) -> str:
        """Detect correct geckodriver path cross-platform."""
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path in [
            os.path.join(project_dir, "..", "geckodriver.exe"),
            os.path.join(project_dir, "..", "geckodriver"),
            "geckodriver.exe", "geckodriver"
        ]:
            if os.path.exists(path):
                return path
        return "geckodriver.exe" if platform.system() == "Windows" else "geckodriver"

    def _configure_profile(self, profile: FirefoxProfile):
        """Configure anti-detection Firefox profile settings."""
        user_agent = get_random_user_agent()
        profile.set_preference("privacy.trackingprotection.enabled", False)
        profile.set_preference("privacy.trackingprotection.pbm.enabled", False)
        profile.set_preference("privacy.trackingprotection.cryptomining.enabled", False)
        profile.set_preference("privacy.trackingprotection.fingerprinting.enabled", False)
        profile.set_preference("media.peerconnection.enabled", False)  # WebRTC
        profile.set_preference("webgl.disabled", True)
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        profile.set_preference("app.update.auto", False)
        profile.set_preference("app.update.enabled", False)
        profile.set_preference("toolkit.telemetry.enabled", False)
        profile.set_preference("toolkit.telemetry.unified", False)
        profile.set_preference("toolkit.telemetry.archive.enabled", False)
        profile.set_preference("general.useragent.override", user_agent)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        profile.set_preference("intl.accept_languages", "en-US, en")
        profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision.microseconds", random.randint(2000, 20000))
        profile.set_preference("privacy.resistFingerprinting.reduceTimerPrecision", True)
        # Random timezone – not always respected, but harmless
        profile.set_preference("timezone", random.choice([
            "America/New_York", "Europe/London", "Asia/Tokyo", "Europe/Moscow", "Asia/Singapore", "Australia/Sydney"
        ]))
        logger.debug("Configured Firefox profile (anti-detection)")

    def _configure_proxy(self, profile: FirefoxProfile):
        """Configure Firefox proxy settings."""
        try:
            parts = self.proxy.split(':')
            ip, port = parts[0], int(parts[1])
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", ip)
            profile.set_preference("network.proxy.http_port", port)
            profile.set_preference("network.proxy.ssl", ip)
            profile.set_preference("network.proxy.ssl_port", port)
            profile.set_preference("network.proxy.no_proxies_on", "localhost,127.0.0.1")
            # Username/password proxies not natively supported in FirefoxProfile—add-on needed if you need it!
            logger.info(f"Proxy set: {ip}:{port}")
        except Exception as e:
            logger.error(f"Proxy config failed: {str(e)}")

    def quit(self):
        """Quit browser and clean up driver/process."""
        if self.driver:
            try:
                self.driver.quit()
                if platform.system() == "Windows":
                    os.system("taskkill /f /im geckodriver.exe /t")
                else:
                    os.system("pkill -f geckodriver")
            except Exception as e:
                logger.error(f"WebDriver quit failed: {str(e)}")
            finally:
                self.driver = None
