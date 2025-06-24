#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proxy Manager Module
-----------------
Manages proxies for browser instances.
"""

import os
import json
import time
import random
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxies for browser instances."""
    
    def __init__(self, proxies: Optional[List[Dict[str, Any]]] = None, config_file: str = "freelancerfly_bot/config/proxies.json"):
        """
        Initialize proxy manager.
        
        Args:
            proxies: List of proxy configurations
            config_file: Path to proxy configuration file
        """
        self.config_file = config_file
        
        # Load proxies from config file if not provided
        if proxies is None:
            self.proxies = self._load_proxies()
        else:
            self.proxies = proxies
            self._save_proxies()
        
        # Initialize proxy usage tracking
        self.proxy_usage = {}
        for i, proxy in enumerate(self.proxies):
            self.proxy_usage[i] = {
                "last_used": 0,
                "usage_count": 0,
                "failures": 0
            }
        
        logger.info(f"Initialized proxy manager with {len(self.proxies)} proxies")
    
    def _load_proxies(self) -> List[Dict[str, Any]]:
        """
        Load proxies from configuration file.
        
        Returns:
            List[Dict[str, Any]]: List of proxy configurations
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    proxies = json.load(f)
                logger.debug(f"Loaded {len(proxies)} proxies from {self.config_file}")
                return proxies
            else:
                logger.warning(f"Proxy configuration file {self.config_file} not found")
                return []
        except Exception as e:
            logger.error(f"Error loading proxies: {str(e)}")
            return []
    
    def _save_proxies(self):
        """Save proxies to configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.proxies, f, indent=2)
            logger.debug(f"Saved {len(self.proxies)} proxies to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving proxies: {str(e)}")
    
    def get_proxy(self) -> Optional[str]:
        """
        Get a proxy for use.
        
        Returns:
            Optional[str]: Proxy string in format "ip:port:username:password", or None if no proxies available
        """
        if not self.proxies:
            logger.warning("No proxies available")
            return None
        
        # Get proxy index based on selection strategy
        proxy_index = self._select_proxy()
        
        if proxy_index is None:
            logger.warning("No suitable proxy found")
            return None
        
        # Get proxy configuration
        proxy = self.proxies[proxy_index]
        
        # Update proxy usage
        self.proxy_usage[proxy_index]["last_used"] = time.time()
        self.proxy_usage[proxy_index]["usage_count"] += 1
        
        # Format proxy string
        proxy_string = self._format_proxy_string(proxy)
        
        logger.debug(f"Selected proxy: {self._mask_proxy_credentials(proxy_string)}")
        
        return proxy_string
    
    def _select_proxy(self) -> Optional[int]:
        """
        Select a proxy based on usage and health.
        
        Returns:
            Optional[int]: Index of selected proxy, or None if no suitable proxy found
        """
        if not self.proxies:
            return None
        
        # Filter out proxies with too many failures
        max_failures = 3
        available_proxies = [i for i, usage in self.proxy_usage.items() if usage["failures"] < max_failures]
        
        if not available_proxies:
            # Reset failure count if all proxies have too many failures
            for i in self.proxy_usage:
                self.proxy_usage[i]["failures"] = 0
            available_proxies = list(range(len(self.proxies)))
        
        # Select proxy based on strategy
        strategy = "least_used"  # Options: "round_robin", "least_used", "random"
        
        if strategy == "round_robin":
            # Select the proxy that was used least recently
            return min(available_proxies, key=lambda i: self.proxy_usage[i]["last_used"])
        
        elif strategy == "least_used":
            # Select the proxy that has been used the least
            return min(available_proxies, key=lambda i: self.proxy_usage[i]["usage_count"])
        
        elif strategy == "random":
            # Select a random proxy
            return random.choice(available_proxies)
        
        else:
            # Default to least used
            return min(available_proxies, key=lambda i: self.proxy_usage[i]["usage_count"])
    
    def _format_proxy_string(self, proxy: Dict[str, Any]) -> str:
        """
        Format proxy configuration as a string.
        
        Args:
            proxy: Proxy configuration
        
        Returns:
            str: Proxy string in format "ip:port:username:password" or "ip:port"
        """
        ip = proxy.get("ip", "")
        port = proxy.get("port", "")
        username = proxy.get("username", "")
        password = proxy.get("password", "")
        
        if username and password:
            return f"{ip}:{port}:{username}:{password}"
        else:
            return f"{ip}:{port}"
    
    def _mask_proxy_credentials(self, proxy_string: str) -> str:
        """
        Mask proxy credentials for logging.
        
        Args:
            proxy_string: Proxy string
        
        Returns:
            str: Masked proxy string
        """
        parts = proxy_string.split(":")
        
        if len(parts) == 4:
            # Mask username and password
            return f"{parts[0]}:{parts[1]}:***:***"
        else:
            return proxy_string
    
    def report_proxy_success(self, proxy_string: str):
        """
        Report successful use of a proxy.
        
        Args:
            proxy_string: Proxy string
        """
        proxy_index = self._find_proxy_index(proxy_string)
        
        if proxy_index is not None:
            # Reset failure count
            self.proxy_usage[proxy_index]["failures"] = 0
            
            logger.debug(f"Proxy {self._mask_proxy_credentials(proxy_string)} used successfully")
    
    def report_proxy_failure(self, proxy_string: str):
        """
        Report failure of a proxy.
        
        Args:
            proxy_string: Proxy string
        """
        proxy_index = self._find_proxy_index(proxy_string)
        
        if proxy_index is not None:
            # Increment failure count
            self.proxy_usage[proxy_index]["failures"] += 1
            
            logger.warning(f"Proxy {self._mask_proxy_credentials(proxy_string)} failed (failures: {self.proxy_usage[proxy_index]['failures']})")
    
    def _find_proxy_index(self, proxy_string: str) -> Optional[int]:
        """
        Find index of a proxy by its string representation.
        
        Args:
            proxy_string: Proxy string
        
        Returns:
            Optional[int]: Index of proxy, or None if not found
        """
        for i, proxy in enumerate(self.proxies):
            if self._format_proxy_string(proxy) == proxy_string:
                return i
        
        return None
    
    def test_proxy(self, proxy_string: str) -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy_string: Proxy string
        
        Returns:
            bool: True if proxy is working, False otherwise
        """
        try:
            # Parse proxy string
            parts = proxy_string.split(":")
            
            if len(parts) == 2:
                # No authentication
                proxy_url = f"http://{parts[0]}:{parts[1]}"
                proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
            elif len(parts) == 4:
                # With authentication
                proxy_url = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
            else:
                logger.warning(f"Invalid proxy format: {self._mask_proxy_credentials(proxy_string)}")
                return False
            
            # Test proxy with a request to a reliable service
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxies,
                timeout=10
            )
            
            # Check if response is successful
            if response.status_code == 200:
                logger.debug(f"Proxy {self._mask_proxy_credentials(proxy_string)} is working")
                return True
            else:
                logger.warning(f"Proxy {self._mask_proxy_credentials(proxy_string)} returned status code {response.status_code}")
                return False
        
        except Exception as e:
            logger.warning(f"Error testing proxy {self._mask_proxy_credentials(proxy_string)}: {str(e)}")
            return False
    
    def test_all_proxies(self) -> Dict[str, bool]:
        """
        Test all proxies.
        
        Returns:
            Dict[str, bool]: Dictionary mapping proxy strings to test results
        """
        results = {}
        
        for i, proxy in enumerate(self.proxies):
            proxy_string = self._format_proxy_string(proxy)
            results[proxy_string] = self.test_proxy(proxy_string)
        
        # Log results
        working_count = sum(1 for result in results.values() if result)
        logger.info(f"Tested {len(results)} proxies, {working_count} working")
        
        return results
    
    def add_proxy(self, proxy: Dict[str, Any]):
        """
        Add a new proxy.
        
        Args:
            proxy: Proxy configuration
        """
        # Validate proxy
        required_fields = ["ip", "port"]
        for field in required_fields:
            if field not in proxy:
                logger.warning(f"Proxy missing required field: {field}")
                return
        
        # Add proxy
        self.proxies.append(proxy)
        
        # Initialize usage tracking
        self.proxy_usage[len(self.proxies) - 1] = {
            "last_used": 0,
            "usage_count": 0,
            "failures": 0
        }
        
        # Save proxies
        self._save_proxies()
        
        logger.info(f"Added new proxy: {proxy['ip']}:{proxy['port']}")
    
    def remove_proxy(self, proxy_string: str):
        """
        Remove a proxy.
        
        Args:
            proxy_string: Proxy string
        """
        proxy_index = self._find_proxy_index(proxy_string)
        
        if proxy_index is not None:
            # Remove proxy
            del self.proxies[proxy_index]
            
            # Update usage tracking
            new_usage = {}
            for i, usage in self.proxy_usage.items():
                if i < proxy_index:
                    new_usage[i] = usage
                elif i > proxy_index:
                    new_usage[i - 1] = usage
            
            self.proxy_usage = new_usage
            
            # Save proxies
            self._save_proxies()
            
            logger.info(f"Removed proxy: {self._mask_proxy_credentials(proxy_string)}")
        else:
            logger.warning(f"Proxy not found: {self._mask_proxy_credentials(proxy_string)}")
    
    def get_proxy_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all proxies.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping proxy strings to statistics
        """
        stats = {}
        
        for i, proxy in enumerate(self.proxies):
            proxy_string = self._format_proxy_string(proxy)
            masked_proxy = self._mask_proxy_credentials(proxy_string)
            
            stats[masked_proxy] = {
                "last_used": self.proxy_usage[i]["last_used"],
                "usage_count": self.proxy_usage[i]["usage_count"],
                "failures": self.proxy_usage[i]["failures"]
            }
        
        return stats