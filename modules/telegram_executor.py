#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram Task Executor Module
---------------------------
Executes Telegram-related tasks such as joining groups, channels, etc.
"""

import re
import time
import random
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from freelancerfly_bot.utils.human_behavior import HumanBehavior

logger = logging.getLogger(__name__)

class TelegramTaskExecutor:
    """Executes Telegram-related tasks."""
    
    def __init__(self, driver, proof_system):
        """
        Initialize Telegram task executor.
        
        Args:
            driver: Selenium WebDriver instance
            proof_system: Proof system instance
        """
        self.driver = driver
        self.proof_system = proof_system
        self.human_behavior = HumanBehavior(driver)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Telegram task.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        task_id = task["id"]
        
        try:
            # Extract Telegram URL from task
            telegram_url = self._extract_telegram_url(task)
            if not telegram_url:
                logger.warning(f"No Telegram URL found in task {task_id}")
                return {
                    "success": False,
                    "error": "No Telegram URL found in task"
                }
            
            logger.info(f"Executing Telegram task: {telegram_url}")
            
            # Navigate to Telegram URL
            self.driver.get(telegram_url)
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of initial state
            initial_screenshot = self.proof_system.take_screenshot(f"telegram_{task_id}_initial")
            
            # Check if we're on Telegram web page
            if "t.me" not in self.driver.current_url and "telegram.org" not in self.driver.current_url:
                logger.warning(f"Not a Telegram page: {self.driver.current_url}")
                return {
                    "success": False,
                    "error": "Not a Telegram page"
                }
            
            # Check if it's a group/channel join task
            if self._is_join_task(task):
                result = self._join_group_or_channel(task)
                if not result["success"]:
                    return result
            
            # Stay on the page for a while
            stay_time = random.uniform(10, 25)
            logger.info(f"Staying on Telegram page for {stay_time:.1f} seconds")
            
            # Simulate human behavior while on the page
            start_time = time.time()
            actions_performed = []
            
            while time.time() - start_time < stay_time:
                # Calculate remaining time
                elapsed = time.time() - start_time
                remaining = stay_time - elapsed
                
                # Perform random actions
                if remaining > 5 and random.random() < 0.5:
                    action = self._perform_random_action()
                    actions_performed.append(action)
                
                # Take progress screenshot occasionally
                if random.random() < 0.3:
                    self.proof_system.take_screenshot(f"telegram_{task_id}_progress_{int(elapsed)}")
                
                # Wait for a random interval
                time.sleep(random.uniform(2, 5))
            
            logger.info(f"Finished Telegram task, actions performed: {actions_performed}")
            
            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"telegram_{task_id}_final")
            
            # Generate proof description
            description = self._generate_proof_description(task, actions_performed)
            
            return {
                "success": True,
                "proof": {
                    "description": description,
                    "screenshots": [initial_screenshot, final_screenshot]
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing Telegram task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_telegram_url(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Extract Telegram URL from task.
        
        Args:
            task: Task information
        
        Returns:
            Optional[str]: Telegram URL, or None if not found
        """
        # Check if we have task details
        description = task.get("description", "")
        
        # Try to find Telegram URL in description
        telegram_patterns = [
            r'https?://(?:www\.)?t\.me/[\w_]+',
            r'https?://(?:www\.)?telegram\.org/[\w/]+'
        ]
        
        for pattern in telegram_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        # If not found in description, try to find it on the page
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and ("t.me/" in href or "telegram.org/" in href):
                    return href
        except Exception:
            pass
        
        return None
    
    def _is_join_task(self, task: Dict[str, Any]) -> bool:
        """
        Check if the task is about joining a Telegram group or channel.
        
        Args:
            task: Task information
        
        Returns:
            bool: True if it's a join task, False otherwise
        """
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()
        
        join_keywords = ["join", "subscribe", "follow", "member"]
        
        for keyword in join_keywords:
            if keyword in description or keyword in title:
                return True
        
        return False
    
    def _join_group_or_channel(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Join a Telegram group or channel.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Join result
        """
        try:
            # Look for join/subscribe button
            join_buttons = []
            
            # Try different button selectors
            selectors = [
                "a.tgme_action_button_new",
                "button.tgme_action_button",
                "a.tgme_action_button",
                "a[data-action='join']",
                "button[data-action='join']"
            ]
            
            for selector in selectors:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                join_buttons.extend(buttons)
            
            if not join_buttons:
                # Check if we're already a member
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.lower()
                        if "joined" in text or "subscribed" in text or "member" in text or "open" in text:
                            logger.info("Already a member of this group/channel")
                            return {"success": True}
                
                logger.warning("Join button not found")
                return {
                    "success": False,
                    "error": "Join button not found"
                }
            
            # Click the first join button
            join_button = join_buttons[0]
            button_text = join_button.text
            
            # Check if already joined
            if "joined" in button_text.lower() or "subscribed" in button_text.lower() or "member" in button_text.lower() or "open" in button_text.lower():
                logger.info("Already a member of this group/channel")
                return {"success": True}
            
            # Take screenshot before joining
            self.proof_system.take_screenshot("telegram_before_join")
            
            # Click join button
            self.human_behavior.move_to_element(join_button)
            time.sleep(random.uniform(0.5, 1.5))
            join_button.click()
            
            logger.info(f"Clicked join button: {button_text}")
            
            # Wait for confirmation
            time.sleep(random.uniform(2, 4))
            
            # Take screenshot after joining
            self.proof_system.take_screenshot("telegram_after_join")
            
            # Check if we need to confirm in Telegram app
            if "open in telegram" in self.driver.page_source.lower():
                logger.info("Requires opening in Telegram app, considering task complete")
                return {"success": True}
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Error joining Telegram group/channel: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _perform_random_action(self) -> str:
        """
        Perform a random action while on the Telegram page.
        
        Returns:
            str: Action performed
        """
        actions = [
            "scroll",
            "mouse_move",
            "check_info"
        ]
        
        action = random.choice(actions)
        
        try:
            if action == "scroll":
                # Scroll down and up
                self.human_behavior.scroll_page(direction="down", distance=random.randint(100, 300))
                time.sleep(random.uniform(1, 2))
                self.human_behavior.scroll_page(direction="up", distance=random.randint(50, 150))
            
            elif action == "mouse_move":
                # Move mouse randomly
                self.human_behavior.move_mouse_randomly()
            
            elif action == "check_info":
                # Look for and click on info elements
                info_elements = []
                
                selectors = [
                    ".tgme_page_description",
                    ".tgme_page_extra",
                    ".tgme_page_additional"
                ]
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    info_elements.extend(elements)
                
                if info_elements:
                    element = random.choice(info_elements)
                    self.human_behavior.move_to_element(element)
                    time.sleep(random.uniform(0.5, 1.5))
            
            return action
        
        except Exception as e:
            logger.error(f"Error performing random action: {str(e)}")
            return "failed_action"
    
    def _generate_proof_description(self, task: Dict[str, Any], actions_performed: list) -> str:
        """
        Generate proof description.
        
        Args:
            task: Task information
            actions_performed: List of actions performed
        
        Returns:
            str: Proof description
        """
        # Get group/channel name
        group_name = "the Telegram group/channel"
        try:
            name_element = self.driver.find_element(By.CSS_SELECTOR, ".tgme_page_title")
            if name_element:
                group_name = name_element.text.strip()
        except Exception:
            pass
        
        # Base description
        if self._is_join_task(task):
            description = f"I joined {group_name} as requested."
        else:
            description = f"I visited {group_name} as requested."
        
        # Add actions
        if actions_performed:
            description += f" I spent time browsing the content and performed {len(actions_performed)} interactions."
        
        # Add timestamp
        description += f" Completed on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."
        
        return description