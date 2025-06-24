#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visit Task Executor Module
-----------------------
Executes visit-related tasks such as visiting websites and browsing pages.
"""

import re
import time
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from freelancerfly_bot.utils.human_behavior import HumanBehavior

logger = logging.getLogger(__name__)

class VisitTaskExecutor:
    """Executes visit-related tasks."""
    
    def __init__(self, driver, proof_system):
        """
        Initialize visit task executor.
        
        Args:
            driver: Selenium WebDriver instance
            proof_system: Proof system instance
        """
        self.driver = driver
        self.proof_system = proof_system
        self.human_behavior = HumanBehavior(driver)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a visit task.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        task_id = task["id"]
        
        try:
            # Extract visit URL from task
            visit_url = self._extract_visit_url(task)
            if not visit_url:
                logger.warning(f"No visit URL found in task {task_id}")
                return {
                    "success": False,
                    "error": "No visit URL found in task"
                }
            
            logger.info(f"Executing visit task: {visit_url}")
            
            # Navigate to visit URL
            self.driver.get(visit_url)
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of initial state
            initial_screenshot = self.proof_system.take_screenshot(f"visit_{task_id}_initial")
            
            # Check if page loaded successfully
            if not self._is_page_loaded():
                logger.warning(f"Page failed to load: {visit_url}")
                return {
                    "success": False,
                    "error": "Page failed to load"
                }
            
            # Determine how many pages to visit (3-5)
            num_pages = random.randint(3, 5)
            
            # Visit pages
            visited_pages = [visit_url]
            screenshots = [initial_screenshot]
            
            for i in range(num_pages):
                # Simulate browsing current page
                self._simulate_browsing_page()
                
                # Take screenshot of current page
                screenshot = self.proof_system.take_screenshot(f"visit_{task_id}_page_{i+1}")
                screenshots.append(screenshot)
                
                # Find links to click
                next_link = self._find_next_link(visited_pages)
                if not next_link:
                    logger.info("No more links to visit")
                    break
                
                # Click link
                link_url = next_link.get_attribute("href")
                
                # Scroll to link
                self.human_behavior.scroll_to_element(next_link)
                time.sleep(random.uniform(1, 2))
                
                # Click link
                self.human_behavior.move_to_element(next_link)
                time.sleep(random.uniform(0.5, 1))
                next_link.click()
                
                # Wait for page to load
                time.sleep(random.uniform(3, 5))
                
                # Check if page loaded successfully
                if not self._is_page_loaded():
                    logger.warning(f"Page failed to load: {link_url}")
                    # Go back to previous page
                    self.driver.back()
                    time.sleep(random.uniform(2, 3))
                    continue
                
                # Add page to visited pages
                current_url = self.driver.current_url
                visited_pages.append(current_url)
                
                logger.info(f"Visited page: {current_url}")
            
            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"visit_{task_id}_final")
            screenshots.append(final_screenshot)
            
            # Generate proof description
            description = self._generate_proof_description(task, visited_pages)
            
            return {
                "success": True,
                "proof": {
                    "description": description,
                    "screenshots": screenshots
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing visit task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_visit_url(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Extract visit URL from task.
        
        Args:
            task: Task information
        
        Returns:
            Optional[str]: Visit URL, or None if not found
        """
        # Check if we have task details
        description = task.get("description", "")
        
        # Try to find URL in description
        url_pattern = r'https?://[^\s<>"\'()]+'
        
        match = re.search(url_pattern, description)
        if match:
            return match.group(0)
        
        # If not found in description, try to find it on the page
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and href.startswith("http"):
                    link_text = link.text.lower()
                    if any(keyword in link_text for keyword in ["visit", "website", "link", "click", "here"]):
                        return href
        except Exception:
            pass
        
        return None
    
    def _is_page_loaded(self) -> bool:
        """
        Check if page is loaded successfully.
        
        Returns:
            bool: True if page is loaded, False otherwise
        """
        try:
            # Check if page has body
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # Check if page has content
            if not body.text.strip():
                return False
            
            # Check for common error indicators
            error_indicators = [
                "404", "not found", "page not found",
                "403", "forbidden",
                "500", "internal server error",
                "service unavailable",
                "bad gateway",
                "gateway timeout",
                "connection refused"
            ]
            
            page_text = body.text.lower()
            page_title = self.driver.title.lower()
            
            for indicator in error_indicators:
                if indicator in page_text or indicator in page_title:
                    return False
            
            return True
        
        except Exception:
            return False
    
    def _simulate_browsing_page(self):
        """Simulate browsing a page."""
        # Determine browsing time (15-30 seconds)
        browsing_time = random.uniform(15, 30)
        
        logger.info(f"Browsing page for {browsing_time:.1f} seconds")
        
        start_time = time.time()
        
        while time.time() - start_time < browsing_time:
            # Choose a random action
            action = random.choice(["scroll", "mouse_move", "pause"])
            
            if action == "scroll":
                # Scroll down or up
                direction = random.choice(["down", "up"])
                distance = random.randint(100, 500)
                
                self.human_behavior.scroll_page(direction=direction, distance=distance)
            
            elif action == "mouse_move":
                # Move mouse randomly
                self.human_behavior.move_mouse_randomly()
            
            elif action == "pause":
                # Pause for a moment
                pass
            
            # Wait between actions
            time.sleep(random.uniform(1, 3))
    
    def _find_next_link(self, visited_pages: List[str]) -> Optional[Any]:
        """
        Find a link to visit next.
        
        Args:
            visited_pages: List of already visited pages
        
        Returns:
            Optional[Any]: Link element, or None if no suitable link found
        """
        try:
            # Get all links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            # Filter links
            valid_links = []
            
            for link in links:
                try:
                    # Get link URL
                    href = link.get_attribute("href")
                    
                    # Skip if no href
                    if not href:
                        continue
                    
                    # Skip if not http(s)
                    if not href.startswith("http"):
                        continue
                    
                    # Skip if already visited
                    if href in visited_pages:
                        continue
                    
                    # Skip if external domain
                    if not self._is_same_domain(href, self.driver.current_url):
                        continue
                    
                    # Skip if not visible
                    if not self._is_element_visible(link):
                        continue
                    
                    # Add to valid links
                    valid_links.append(link)
                
                except Exception:
                    continue
            
            # If no valid links, try to find links with different criteria
            if not valid_links:
                for link in links:
                    try:
                        # Get link URL
                        href = link.get_attribute("href")
                        
                        # Skip if no href
                        if not href:
                            continue
                        
                        # Skip if not http(s)
                        if not href.startswith("http"):
                            continue
                        
                        # Skip if already visited
                        if href in visited_pages:
                            continue
                        
                        # Skip if not visible
                        if not self._is_element_visible(link):
                            continue
                        
                        # Add to valid links
                        valid_links.append(link)
                    
                    except Exception:
                        continue
            
            # If still no valid links, return None
            if not valid_links:
                return None
            
            # Choose a random link
            return random.choice(valid_links)
        
        except Exception as e:
            logger.error(f"Error finding next link: {str(e)}")
            return None
    
    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs have the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
        
        Returns:
            bool: True if same domain, False otherwise
        """
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            
            # Remove www. prefix
            domain1 = domain1.replace("www.", "")
            domain2 = domain2.replace("www.", "")
            
            return domain1 == domain2
        
        except Exception:
            return False
    
    def _is_element_visible(self, element) -> bool:
        """
        Check if an element is visible.
        
        Args:
            element: Element to check
        
        Returns:
            bool: True if element is visible, False otherwise
        """
        try:
            return element.is_displayed() and element.is_enabled()
        except Exception:
            return False
    
    def _generate_proof_description(self, task: Dict[str, Any], visited_pages: List[str]) -> str:
        """
        Generate proof description.
        
        Args:
            task: Task information
            visited_pages: List of visited pages
        
        Returns:
            str: Proof description
        """
        # Get domain
        if visited_pages:
            domain = self._extract_domain(visited_pages[0])
        else:
            domain = "the website"
        
        # Base description
        description = f"I visited {domain} as requested."
        
        # Add details about visited pages
        if len(visited_pages) > 1:
            description += f" I browsed through {len(visited_pages)} pages on the website, spending time on each page and interacting with the content."
        else:
            description += f" I spent time on the website, scrolling through the content and exploring the page."
        
        # Add timestamp
        description += f" Completed on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."
        
        return description
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL
        
        Returns:
            str: Domain
        """
        try:
            domain = urlparse(url).netloc
            
            # Remove www. prefix
            domain = domain.replace("www.", "")
            
            return domain
        
        except Exception:
            return "the website"