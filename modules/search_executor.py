#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search Task Executor Module
-------------------------
Executes search-related tasks such as searching on Google, Bing, etc.
"""

import re
import time
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from freelancerfly_bot.utils.human_behavior import HumanBehavior

logger = logging.getLogger(__name__)

class SearchTaskExecutor:
    """Executes search-related tasks."""
    
    # Search engines
    SEARCH_ENGINE_GOOGLE = "google"
    SEARCH_ENGINE_BING = "bing"
    SEARCH_ENGINE_YAHOO = "yahoo"
    SEARCH_ENGINE_DUCKDUCKGO = "duckduckgo"
    
    def __init__(self, driver, proof_system):
        """
        Initialize search task executor.
        
        Args:
            driver: Selenium WebDriver instance
            proof_system: Proof system instance
        """
        self.driver = driver
        self.proof_system = proof_system
        self.human_behavior = HumanBehavior(driver)
        
        # Search engine URLs
        self.search_engine_urls = {
            self.SEARCH_ENGINE_GOOGLE: "https://www.google.com",
            self.SEARCH_ENGINE_BING: "https://www.bing.com",
            self.SEARCH_ENGINE_YAHOO: "https://search.yahoo.com",
            self.SEARCH_ENGINE_DUCKDUCKGO: "https://duckduckgo.com"
        }
        
        # Search input selectors
        self.search_input_selectors = {
            self.SEARCH_ENGINE_GOOGLE: "input[name='q']",
            self.SEARCH_ENGINE_BING: "input[name='q']",
            self.SEARCH_ENGINE_YAHOO: "input[name='p']",
            self.SEARCH_ENGINE_DUCKDUCKGO: "input[name='q']"
        }
        
        # Search result selectors
        self.search_result_selectors = {
            self.SEARCH_ENGINE_GOOGLE: ".g a",
            self.SEARCH_ENGINE_BING: ".b_algo a",
            self.SEARCH_ENGINE_YAHOO: ".algo a",
            self.SEARCH_ENGINE_DUCKDUCKGO: ".result__a"
        }
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a search task.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        task_id = task["id"]
        
        try:
            # Extract search query and engine from task
            search_query, search_engine = self._extract_search_info(task)
            if not search_query:
                logger.warning(f"No search query found in task {task_id}")
                return {
                    "success": False,
                    "error": "No search query found in task"
                }
            
            logger.info(f"Executing search task: {search_query} on {search_engine}")
            
            # Navigate to search engine
            search_engine_url = self.search_engine_urls.get(search_engine, self.search_engine_urls[self.SEARCH_ENGINE_GOOGLE])
            self.driver.get(search_engine_url)
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of initial state
            initial_screenshot = self.proof_system.take_screenshot(f"search_{task_id}_initial")
            
            # Perform search
            search_result = self._perform_search(search_engine, search_query)
            if not search_result["success"]:
                return search_result
            
            # Take screenshot of search results
            search_results_screenshot = self.proof_system.take_screenshot(f"search_{task_id}_results")
            
            # Click on search results
            click_result = self._click_search_results(search_engine)
            if not click_result["success"]:
                return click_result
            
            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"search_{task_id}_final")
            
            # Generate proof description
            description = self._generate_proof_description(task, search_query, search_engine, click_result)
            
            return {
                "success": True,
                "proof": {
                    "description": description,
                    "screenshots": [initial_screenshot, search_results_screenshot, final_screenshot]
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing search task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_search_info(self, task: Dict[str, Any]) -> tuple:
        """
        Extract search query and engine from task.
        
        Args:
            task: Task information
        
        Returns:
            tuple: (search_query, search_engine)
        """
        # Check if we have task details
        description = task.get("description", "")
        title = task.get("title", "")
        
        # Try to find search query
        search_query = None
        
        # Look for specific patterns
        search_patterns = [
            r'search for ["\']([^"\']+)["\']',
            r'search ["\']([^"\']+)["\']',
            r'search for (.+?)(?:on|in|using|$)',
            r'search (.+?)(?:on|in|using|$)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                search_query = match.group(1).strip()
                break
        
        # If not found, use the title as a fallback
        if not search_query and title:
            search_query = title
        
        # Determine search engine
        search_engine = self.SEARCH_ENGINE_GOOGLE  # Default to Google
        
        if "google" in description.lower():
            search_engine = self.SEARCH_ENGINE_GOOGLE
        elif "bing" in description.lower():
            search_engine = self.SEARCH_ENGINE_BING
        elif "yahoo" in description.lower():
            search_engine = self.SEARCH_ENGINE_YAHOO
        elif "duckduckgo" in description.lower() or "duck duck go" in description.lower():
            search_engine = self.SEARCH_ENGINE_DUCKDUCKGO
        
        return search_query, search_engine
    
    def _perform_search(self, search_engine: str, search_query: str) -> Dict[str, Any]:
        """
        Perform a search on the specified search engine.
        
        Args:
            search_engine: Search engine
            search_query: Search query
        
        Returns:
            Dict[str, Any]: Search result
        """
        try:
            # Find search input
            search_input_selector = self.search_input_selectors.get(search_engine)
            if not search_input_selector:
                logger.warning(f"No search input selector for {search_engine}")
                return {
                    "success": False,
                    "error": f"No search input selector for {search_engine}"
                }
            
            try:
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, search_input_selector))
                )
            except TimeoutException:
                logger.warning(f"Search input not found for {search_engine}")
                return {
                    "success": False,
                    "error": f"Search input not found for {search_engine}"
                }
            
            # Click on search input
            self.human_behavior.move_to_element(search_input)
            time.sleep(random.uniform(0.5, 1))
            search_input.click()
            time.sleep(random.uniform(0.5, 1))
            
            # Type search query with human-like delays
            self.human_behavior.type_text(search_input, search_query)
            time.sleep(random.uniform(0.5, 1))
            
            # Press Enter to search
            search_input.send_keys(Keys.RETURN)
            
            # Wait for search results
            time.sleep(random.uniform(3, 5))
            
            logger.info(f"Performed search: {search_query} on {search_engine}")
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _click_search_results(self, search_engine: str) -> Dict[str, Any]:
        """
        Click on search results.
        
        Args:
            search_engine: Search engine
        
        Returns:
            Dict[str, Any]: Click result
        """
        try:
            # Find search results
            search_result_selector = self.search_result_selectors.get(search_engine)
            if not search_result_selector:
                logger.warning(f"No search result selector for {search_engine}")
                return {
                    "success": False,
                    "error": f"No search result selector for {search_engine}"
                }
            
            try:
                search_results = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, search_result_selector))
                )
            except TimeoutException:
                logger.warning(f"Search results not found for {search_engine}")
                return {
                    "success": False,
                    "error": f"Search results not found for {search_engine}"
                }
            
            # Filter out ads and other non-result links
            filtered_results = []
            for result in search_results:
                href = result.get_attribute("href")
                if href and not self._is_ad_link(href, search_engine):
                    filtered_results.append(result)
            
            if not filtered_results:
                logger.warning("No valid search results found")
                return {
                    "success": False,
                    "error": "No valid search results found"
                }
            
            # Determine how many results to click (1-2)
            num_clicks = random.randint(1, min(2, len(filtered_results)))
            
            clicked_links = []
            
            for i in range(num_clicks):
                # Choose a result to click
                result_index = random.randint(0, min(5, len(filtered_results) - 1))
                result = filtered_results[result_index]
                
                # Get result URL
                result_url = result.get_attribute("href")
                
                # Scroll to result
                self.human_behavior.scroll_to_element(result)
                time.sleep(random.uniform(1, 2))
                
                # Take screenshot before clicking
                self.proof_system.take_screenshot(f"search_result_{i+1}_before_click")
                
                # Click result
                self.human_behavior.move_to_element(result)
                time.sleep(random.uniform(0.5, 1))
                
                # Open in new tab
                if i < num_clicks - 1:
                    # Middle click to open in new tab
                    self.human_behavior.middle_click_element(result)
                else:
                    # Regular click for the last result
                    result.click()
                
                logger.info(f"Clicked search result: {result_url}")
                clicked_links.append(result_url)
                
                # Wait for page to load
                time.sleep(random.uniform(5, 8))
                
                # Simulate reading the page
                self._simulate_reading_page()
                
                # Take screenshot of the page
                self.proof_system.take_screenshot(f"search_result_{i+1}_page")
                
                # Go back to search results for the next click
                if i < num_clicks - 1:
                    self.driver.back()
                    time.sleep(random.uniform(2, 3))
            
            return {
                "success": True,
                "clicked_links": clicked_links,
                "num_clicks": num_clicks
            }
        
        except Exception as e:
            logger.error(f"Error clicking search results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_ad_link(self, url: str, search_engine: str) -> bool:
        """
        Check if a URL is an ad link.
        
        Args:
            url: URL to check
            search_engine: Search engine
        
        Returns:
            bool: True if URL is an ad link, False otherwise
        """
        # Google ad patterns
        if search_engine == self.SEARCH_ENGINE_GOOGLE:
            return "google.com/aclk" in url or "googleadservices.com" in url
        
        # Bing ad patterns
        elif search_engine == self.SEARCH_ENGINE_BING:
            return "bing.com/aclick" in url or "msn.com/en-us/marketplace" in url
        
        # Yahoo ad patterns
        elif search_engine == self.SEARCH_ENGINE_YAHOO:
            return "yahoo.com/adclick" in url
        
        # DuckDuckGo ad patterns
        elif search_engine == self.SEARCH_ENGINE_DUCKDUCKGO:
            return "duck.co/y" in url
        
        return False
    
    def _simulate_reading_page(self):
        """Simulate reading a page."""
        # Scroll down slowly
        scroll_iterations = random.randint(3, 7)
        
        for _ in range(scroll_iterations):
            # Scroll down
            self.human_behavior.scroll_page(direction="down", distance=random.randint(300, 600))
            
            # Wait between scrolls
            time.sleep(random.uniform(2, 5))
            
            # Move mouse randomly
            if random.random() < 0.3:
                self.human_behavior.move_mouse_randomly()
        
        # Scroll back up sometimes
        if random.random() < 0.5:
            self.human_behavior.scroll_page(direction="up", distance=random.randint(200, 500))
            time.sleep(random.uniform(1, 3))
    
    def _generate_proof_description(self, task: Dict[str, Any], search_query: str, search_engine: str, click_result: Dict[str, Any]) -> str:
        """
        Generate proof description.
        
        Args:
            task: Task information
            search_query: Search query
            search_engine: Search engine
            click_result: Click result
        
        Returns:
            str: Proof description
        """
        # Format search engine name
        search_engine_names = {
            self.SEARCH_ENGINE_GOOGLE: "Google",
            self.SEARCH_ENGINE_BING: "Bing",
            self.SEARCH_ENGINE_YAHOO: "Yahoo",
            self.SEARCH_ENGINE_DUCKDUCKGO: "DuckDuckGo"
        }
        
        search_engine_name = search_engine_names.get(search_engine, search_engine.capitalize())
        
        # Base description
        description = f"I searched for '{search_query}' on {search_engine_name}."
        
        # Add clicked links
        clicked_links = click_result.get("clicked_links", [])
        num_clicks = click_result.get("num_clicks", 0)
        
        if clicked_links:
            if len(clicked_links) == 1:
                description += f" I clicked on 1 search result and spent time reading the page."
            else:
                description += f" I clicked on {len(clicked_links)} search results and spent time reading each page."
        
        # Add timestamp
        description += f" Completed on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."
        
        return description