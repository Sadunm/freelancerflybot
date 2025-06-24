#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Human Behavior Module
------------------
Simulates human-like behavior for browser interactions.
"""

import time
import random
import logging
import math
from typing import Optional, Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import MoveTargetOutOfBoundsException

logger = logging.getLogger(__name__)

class HumanBehavior:
    """Simulates human-like behavior for browser interactions."""
    
    def __init__(self, driver):
        """
        Initialize human behavior simulator.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.action_chains = ActionChains(driver)
        self.screen_width = 1366  # Default screen width
        self.screen_height = 768  # Default screen height
        
        # Try to get actual window size
        try:
            size = driver.get_window_size()
            self.screen_width = size['width']
            self.screen_height = size['height']
        except Exception:
            pass
    
    def move_to_element(self, element):
        """
        Move mouse to an element with human-like motion.
        
        Args:
            element: Element to move to
        """
        try:
            # Get element location
            location = element.location
            size = element.size
            
            # Calculate target coordinates (center of element)
            target_x = location['x'] + size['width'] // 2
            target_y = location['y'] + size['height'] // 2
            
            # Get current mouse position
            current_x, current_y = self._get_current_mouse_position()
            
            # Move mouse with Bezier curve
            self._move_mouse_with_bezier(current_x, current_y, target_x, target_y)
        
        except Exception as e:
            logger.error(f"Error moving to element: {str(e)}")
            
            # Fallback to regular move_to_element
            try:
                self.action_chains.move_to_element(element).perform()
            except Exception as e2:
                logger.error(f"Error in fallback move_to_element: {str(e2)}")
    
    def move_mouse_randomly(self, max_distance: int = 200):
        """
        Move mouse randomly.
        
        Args:
            max_distance: Maximum distance to move
        """
        try:
            # Get current mouse position
            current_x, current_y = self._get_current_mouse_position()
            
            # Calculate random target coordinates
            target_x = max(0, min(current_x + random.randint(-max_distance, max_distance), self.screen_width))
            target_y = max(0, min(current_y + random.randint(-max_distance, max_distance), self.screen_height))
            
            # Move mouse with Bezier curve
            self._move_mouse_with_bezier(current_x, current_y, target_x, target_y)
        
        except Exception as e:
            logger.error(f"Error moving mouse randomly: {str(e)}")
    
    def scroll_page(self, direction: str = "down", distance: int = 300):
        """
        Scroll page with human-like behavior.
        
        Args:
            direction: Scroll direction ("up" or "down")
            distance: Scroll distance in pixels
        """
        try:
            # Determine scroll direction
            scroll_direction = -1 if direction == "up" else 1
            
            # Calculate scroll steps
            num_steps = random.randint(5, 10)
            step_distance = distance // num_steps
            
            # Scroll with steps
            for _ in range(num_steps):
                # Calculate step distance with randomness
                actual_step = step_distance + random.randint(-10, 10)
                
                # Execute scroll
                self.driver.execute_script(f"window.scrollBy(0, {actual_step * scroll_direction})")
                
                # Wait between steps
                time.sleep(random.uniform(0.01, 0.05))
        
        except Exception as e:
            logger.error(f"Error scrolling page: {str(e)}")
            
            # Fallback to regular scroll
            try:
                self.driver.execute_script(f"window.scrollBy(0, {distance * (-1 if direction == 'up' else 1)})")
            except Exception as e2:
                logger.error(f"Error in fallback scroll: {str(e2)}")
    
    def scroll_to_element(self, element):
        """
        Scroll to an element with human-like behavior.
        
        Args:
            element: Element to scroll to
        """
        try:
            # Get element location
            location = element.location
            
            # Get current scroll position
            current_scroll = self.driver.execute_script("return window.pageYOffset")
            
            # Calculate scroll distance
            scroll_distance = location['y'] - current_scroll - 200  # 200px above element
            
            # Determine scroll direction
            direction = "down" if scroll_distance > 0 else "up"
            
            # Scroll with human-like behavior
            self.scroll_page(direction, abs(scroll_distance))
        
        except Exception as e:
            logger.error(f"Error scrolling to element: {str(e)}")
            
            # Fallback to regular scroll into view
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'})", element)
            except Exception as e2:
                logger.error(f"Error in fallback scroll to element: {str(e2)}")
    
    def type_text(self, element, text: str):
        """
        Type text with human-like delays and occasional typos.
        
        Args:
            element: Element to type in
            text: Text to type
        """
        try:
            # Focus on element
            element.click()
            time.sleep(random.uniform(0.2, 0.5))
            
            # Determine if we should make a typo
            make_typo = random.random() < 0.1  # 10% chance of typo
            
            # Type text with human-like delays
            for i, char in enumerate(text):
                # Type character
                element.send_keys(char)
                
                # Add human-like delay between keystrokes
                time.sleep(random.uniform(0.05, 0.2))
                
                # Make a typo and correct it
                if make_typo and i > 0 and i < len(text) - 2 and random.random() < 0.2:
                    # Type a wrong character
                    wrong_char = self._get_nearby_key(char)
                    element.send_keys(wrong_char)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Delete the wrong character
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Type the correct character
                    element.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Reset typo flag
                    make_typo = False
        
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
            
            # Fallback to regular send_keys
            try:
                element.clear()
                element.send_keys(text)
            except Exception as e2:
                logger.error(f"Error in fallback type text: {str(e2)}")
    
    def middle_click_element(self, element):
        """
        Middle-click an element to open in a new tab.
        
        Args:
            element: Element to middle-click
        """
        try:
            # Create a new action chain
            actions = ActionChains(self.driver)
            
            # Move to element
            self.move_to_element(element)
            time.sleep(random.uniform(0.2, 0.5))
            
            # Middle-click element
            actions.move_to_element(element).click_and_hold(Keys.CONTROL).click().release(Keys.CONTROL).perform()
            
            # Wait for tab to open
            time.sleep(random.uniform(0.5, 1))
        
        except Exception as e:
            logger.error(f"Error middle-clicking element: {str(e)}")
            
            # Fallback to Ctrl+Click
            try:
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
            except Exception as e2:
                logger.error(f"Error in fallback middle-click: {str(e2)}")
    
    def _get_current_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            Tuple[int, int]: Current mouse position (x, y)
        """
        try:
            # Execute JavaScript to get mouse position
            position = self.driver.execute_script("""
                return [
                    window.mouseX || window.lastMouseX || window.innerWidth / 2,
                    window.mouseY || window.lastMouseY || window.innerHeight / 2
                ];
            """)
            
            if position and len(position) == 2:
                return position[0], position[1]
        
        except Exception:
            pass
        
        # Default to center of screen
        return self.screen_width // 2, self.screen_height // 2
    
    def _move_mouse_with_bezier(self, start_x: int, start_y: int, end_x: int, end_y: int, num_steps: int = 20):
        """
        Move mouse with Bezier curve for natural movement.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            num_steps: Number of steps for the movement
        """
        try:
            # Generate control points for Bezier curve
            control_points = self._generate_bezier_control_points(start_x, start_y, end_x, end_y)
            
            # Calculate points along Bezier curve
            points = self._calculate_bezier_points(control_points, num_steps)
            
            # Move mouse along curve
            for point in points:
                x, y = point
                
                # Ensure coordinates are within screen bounds
                x = max(0, min(x, self.screen_width))
                y = max(0, min(y, self.screen_height))
                
                # Move to point
                try:
                    self.action_chains.move_by_offset(x - start_x, y - start_y).perform()
                    start_x, start_y = x, y  # Update start position for next move
                except MoveTargetOutOfBoundsException:
                    # If move is out of bounds, reset action chains and try again
                    self.action_chains = ActionChains(self.driver)
                    self.action_chains.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, 'body'), x, y).perform()
                    start_x, start_y = x, y
                
                # Add small delay between movements
                time.sleep(random.uniform(0.01, 0.03))
        
        except Exception as e:
            logger.error(f"Error moving mouse with Bezier curve: {str(e)}")
            
            # Fallback to direct move
            try:
                self.action_chains = ActionChains(self.driver)
                self.action_chains.move_by_offset(end_x - start_x, end_y - start_y).perform()
            except Exception as e2:
                logger.error(f"Error in fallback mouse move: {str(e2)}")
    
    def _generate_bezier_control_points(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
        """
        Generate control points for Bezier curve.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
        
        Returns:
            List[Tuple[int, int]]: Control points for Bezier curve
        """
        # Calculate distance between start and end points
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        # Calculate control point offset based on distance
        offset = min(100, distance * 0.3)
        
        # Generate random control points
        control1_x = start_x + random.uniform(-offset, offset)
        control1_y = start_y + random.uniform(-offset, offset)
        
        control2_x = end_x + random.uniform(-offset, offset)
        control2_y = end_y + random.uniform(-offset, offset)
        
        # Return control points
        return [(start_x, start_y), (control1_x, control1_y), (control2_x, control2_y), (end_x, end_y)]
    
    def _calculate_bezier_points(self, control_points: List[Tuple[int, int]], num_steps: int) -> List[Tuple[int, int]]:
        """
        Calculate points along Bezier curve.
        
        Args:
            control_points: Control points for Bezier curve
            num_steps: Number of steps
        
        Returns:
            List[Tuple[int, int]]: Points along Bezier curve
        """
        points = []
        
        for i in range(num_steps + 1):
            t = i / num_steps
            
            # Cubic Bezier formula
            x = (1 - t) ** 3 * control_points[0][0] + 3 * (1 - t) ** 2 * t * control_points[1][0] + 3 * (1 - t) * t ** 2 * control_points[2][0] + t ** 3 * control_points[3][0]
            y = (1 - t) ** 3 * control_points[0][1] + 3 * (1 - t) ** 2 * t * control_points[1][1] + 3 * (1 - t) * t ** 2 * control_points[2][1] + t ** 3 * control_points[3][1]
            
            points.append((int(x), int(y)))
        
        return points
    
    def _get_nearby_key(self, char: str) -> str:
        """
        Get a nearby key on the keyboard for realistic typos.
        
        Args:
            char: Character to get nearby key for
        
        Returns:
            str: Nearby key
        """
        # Keyboard layout
        keyboard = {
            'q': ['w', 'a', '1'],
            'w': ['q', 'e', 'a', 's', '2'],
            'e': ['w', 'r', 's', 'd', '3'],
            'r': ['e', 't', 'd', 'f', '4'],
            't': ['r', 'y', 'f', 'g', '5'],
            'y': ['t', 'u', 'g', 'h', '6'],
            'u': ['y', 'i', 'h', 'j', '7'],
            'i': ['u', 'o', 'j', 'k', '8'],
            'o': ['i', 'p', 'k', 'l', '9'],
            'p': ['o', '[', 'l', ';', '0'],
            'a': ['q', 'w', 's', 'z'],
            's': ['w', 'e', 'a', 'd', 'z', 'x'],
            'd': ['e', 'r', 's', 'f', 'x', 'c'],
            'f': ['r', 't', 'd', 'g', 'c', 'v'],
            'g': ['t', 'y', 'f', 'h', 'v', 'b'],
            'h': ['y', 'u', 'g', 'j', 'b', 'n'],
            'j': ['u', 'i', 'h', 'k', 'n', 'm'],
            'k': ['i', 'o', 'j', 'l', 'm', ','],
            'l': ['o', 'p', 'k', ';', ',', '.'],
            'z': ['a', 's', 'x'],
            'x': ['z', 's', 'd', 'c'],
            'c': ['x', 'd', 'f', 'v'],
            'v': ['c', 'f', 'g', 'b'],
            'b': ['v', 'g', 'h', 'n'],
            'n': ['b', 'h', 'j', 'm'],
            'm': ['n', 'j', 'k', ','],
            ',': ['m', 'k', 'l', '.'],
            '.': [',', 'l', ';', '/'],
            '1': ['q', '2'],
            '2': ['1', 'q', 'w', '3'],
            '3': ['2', 'w', 'e', '4'],
            '4': ['3', 'e', 'r', '5'],
            '5': ['4', 'r', 't', '6'],
            '6': ['5', 't', 'y', '7'],
            '7': ['6', 'y', 'u', '8'],
            '8': ['7', 'u', 'i', '9'],
            '9': ['8', 'i', 'o', '0'],
            '0': ['9', 'o', 'p', '-'],
            ' ': ['c', 'v', 'b', 'n', 'm']
        }
        
        # Convert to lowercase
        char_lower = char.lower()
        
        # If character is in keyboard layout, get a random nearby key
        if char_lower in keyboard:
            nearby_keys = keyboard[char_lower]
            nearby_key = random.choice(nearby_keys)
            
            # Preserve case
            if char.isupper():
                return nearby_key.upper()
            else:
                return nearby_key
        
        # If character is not in keyboard layout, return the original character
        return char