#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
YouTube Task Executor Module
--------------------------
Executes YouTube-related tasks such as watching videos, liking, commenting, etc.
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

class YouTubeTaskExecutor:
    """Executes YouTube-related tasks."""
    
    def __init__(self, driver, proof_system):
        """
        Initialize YouTube task executor.
        
        Args:
            driver: Selenium WebDriver instance
            proof_system: Proof system instance
        """
        self.driver = driver
        self.proof_system = proof_system
        self.human_behavior = HumanBehavior(driver)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a YouTube task.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        task_id = task["id"]
        
        try:
            # Extract YouTube URL from task
            youtube_url = self._extract_youtube_url(task)
            if not youtube_url:
                logger.warning(f"No YouTube URL found in task {task_id}")
                return {
                    "success": False,
                    "error": "No YouTube URL found in task"
                }
            
            logger.info(f"Executing YouTube task: {youtube_url}")
            
            # Navigate to YouTube video
            self.driver.get(youtube_url)
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of initial video state
            initial_screenshot = self.proof_system.take_screenshot(f"youtube_{task_id}_initial")
            
            # Check if video is available
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
                )
            except TimeoutException:
                logger.warning(f"Video not available: {youtube_url}")
                return {
                    "success": False,
                    "error": "Video not available"
                }
            
            # Get video duration
            video_duration = self._get_video_duration()
            if not video_duration:
                logger.warning(f"Could not determine video duration: {youtube_url}")
                video_duration = 300  # Default to 5 minutes
            
            # Calculate watch time (120-150% of video duration, capped at 10 minutes)
            watch_percentage = random.uniform(1.2, 1.5)
            watch_time = min(video_duration * watch_percentage, 600)
            
            logger.info(f"Video duration: {video_duration}s, watching for: {watch_time}s")
            
            # Start video if not already playing
            try:
                play_button = self.driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
                if "Play" in play_button.get_attribute("aria-label"):
                    play_button.click()
                    time.sleep(1)
            except NoSuchElementException:
                pass
            
            # Simulate human behavior while watching
            start_time = time.time()
            actions_performed = []
            
            while time.time() - start_time < watch_time:
                # Calculate remaining time
                elapsed = time.time() - start_time
                remaining = watch_time - elapsed
                
                # Perform random actions
                if remaining > 10 and random.random() < 0.3:
                    action = self._perform_random_action()
                    actions_performed.append(action)
                
                # Take progress screenshot occasionally
                if random.random() < 0.2:
                    self.proof_system.take_screenshot(f"youtube_{task_id}_progress_{int(elapsed)}")
                
                # Wait for a random interval
                time.sleep(random.uniform(5, 15))
            
            logger.info(f"Finished watching video, actions performed: {actions_performed}")
            
            # Check if like/comment is required
            if self._should_like_video(task):
                self._like_video()
                actions_performed.append("like")
            
            if self._should_comment_video(task):
                comment = self._generate_comment(task)
                self._comment_video(comment)
                actions_performed.append("comment")
            
            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"youtube_{task_id}_final")
            
            # Record video if required
            video_proof = None
            if self._should_record_video(task):
                video_proof = self.proof_system.record_screen(f"youtube_{task_id}_proof", duration=10)
            
            # Generate proof description
            description = self._generate_proof_description(task, video_duration, actions_performed)
            
            return {
                "success": True,
                "proof": {
                    "description": description,
                    "screenshots": [initial_screenshot, final_screenshot],
                    "video": video_proof
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing YouTube task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_youtube_url(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Extract YouTube URL from task.
        
        Args:
            task: Task information
        
        Returns:
            Optional[str]: YouTube URL, or None if not found
        """
        # Check if we have task details
        description = task.get("description", "")
        
        # Try to find YouTube URL in description
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://(?:www\.)?youtu\.be/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        # If not found in description, try to find it on the page
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and ("youtube.com/watch" in href or "youtu.be/" in href):
                    return href
        except Exception:
            pass
        
        return None
    
    def _get_video_duration(self) -> Optional[int]:
        """
        Get video duration in seconds.
        
        Returns:
            Optional[int]: Video duration in seconds, or None if not found
        """
        try:
            # Wait for duration element
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-time-duration"))
            )
            
            # Get duration text
            duration_element = self.driver.find_element(By.CSS_SELECTOR, ".ytp-time-duration")
            duration_text = duration_element.text.strip()
            
            # Parse duration
            parts = duration_text.split(":")
            if len(parts) == 2:
                # MM:SS format
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                # HH:MM:SS format
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
            return None
    
    def _perform_random_action(self) -> str:
        """
        Perform a random action while watching the video.
        
        Returns:
            str: Action performed
        """
        actions = [
            "scroll",
            "mouse_move",
            "volume_change",
            "pause_play",
            "fullscreen_toggle"
        ]
        
        action = random.choice(actions)
        
        try:
            if action == "scroll":
                # Scroll down and up
                self.human_behavior.scroll_page(direction="down", distance=random.randint(100, 300))
                time.sleep(random.uniform(1, 3))
                self.human_behavior.scroll_page(direction="up", distance=random.randint(50, 200))
            
            elif action == "mouse_move":
                # Move mouse randomly
                self.human_behavior.move_mouse_randomly()
            
            elif action == "volume_change":
                # Change volume
                try:
                    volume_slider = self.driver.find_element(By.CSS_SELECTOR, ".ytp-volume-panel")
                    self.human_behavior.move_to_element(volume_slider)
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Click volume slider
                    volume_slider.click()
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Move mouse to change volume
                    self.human_behavior.move_mouse_randomly(max_distance=50)
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Click again to hide volume slider
                    volume_slider.click()
                except Exception:
                    pass
            
            elif action == "pause_play":
                # Pause and play video
                try:
                    play_button = self.driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
                    self.human_behavior.move_to_element(play_button)
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Click to pause
                    play_button.click()
                    time.sleep(random.uniform(2, 4))
                    
                    # Click to play
                    play_button.click()
                except Exception:
                    pass
            
            elif action == "fullscreen_toggle":
                # Toggle fullscreen
                try:
                    fullscreen_button = self.driver.find_element(By.CSS_SELECTOR, ".ytp-fullscreen-button")
                    self.human_behavior.move_to_element(fullscreen_button)
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Click to enter fullscreen
                    fullscreen_button.click()
                    time.sleep(random.uniform(3, 5))
                    
                    # Click to exit fullscreen
                    fullscreen_button.click()
                except Exception:
                    pass
            
            return action
        
        except Exception as e:
            logger.error(f"Error performing random action: {str(e)}")
            return "failed_action"
    
    def _should_like_video(self, task: Dict[str, Any]) -> bool:
        """
        Check if the task requires liking the video.
        
        Args:
            task: Task information
        
        Returns:
            bool: True if the task requires liking the video, False otherwise
        """
        description = task.get("description", "").lower()
        return "like" in description or "thumbs up" in description
    
    def _should_comment_video(self, task: Dict[str, Any]) -> bool:
        """
        Check if the task requires commenting on the video.
        
        Args:
            task: Task information
        
        Returns:
            bool: True if the task requires commenting on the video, False otherwise
        """
        description = task.get("description", "").lower()
        return "comment" in description
    
    def _should_record_video(self, task: Dict[str, Any]) -> bool:
        """
        Check if the task requires recording a video proof.
        
        Args:
            task: Task information
        
        Returns:
            bool: True if the task requires recording a video proof, False otherwise
        """
        description = task.get("description", "").lower()
        return "record" in description or "video proof" in description
    
    def _like_video(self):
        """Like the video."""
        try:
            # Find like button
            like_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='like']")
            
            # Check if already liked
            if "active" in like_button.get_attribute("class"):
                logger.debug("Video already liked")
                return
            
            # Move to like button
            self.human_behavior.move_to_element(like_button)
            time.sleep(random.uniform(0.5, 1))
            
            # Click like button
            like_button.click()
            logger.info("Liked video")
            
            # Take screenshot
            self.proof_system.take_screenshot("youtube_like_proof")
        
        except Exception as e:
            logger.error(f"Error liking video: {str(e)}")
    
    def _generate_comment(self, task: Dict[str, Any]) -> str:
        """
        Generate a comment for the video.
        
        Args:
            task: Task information
        
        Returns:
            str: Generated comment
        """
        # List of generic positive comments
        comments = [
            "Great video! Thanks for sharing.",
            "Really enjoyed this, very informative.",
            "Thanks for the content, very helpful!",
            "Interesting video, learned something new today.",
            "Nice explanation, well done!",
            "This was exactly what I was looking for, thanks!",
            "Very clear and concise, appreciate it.",
            "Well presented information, thanks for sharing.",
            "This is really useful content, thank you.",
            "Great job on this video, very professional."
        ]
        
        # Add some randomness
        if random.random() < 0.3:
            comments.append(f"Watched this on {datetime.now().strftime('%B %d')}, very helpful!")
        
        if random.random() < 0.3:
            comments.append("Just discovered your channel, will check out more videos!")
        
        # Select a random comment
        comment = random.choice(comments)
        
        # Add emoji occasionally
        if random.random() < 0.4:
            emojis = ["👍", "🙌", "👏", "😊", "👌", "🔥", "💯", "⭐", "✅", "🎯"]
            comment += f" {random.choice(emojis)}"
        
        return comment
    
    def _comment_video(self, comment: str):
        """
        Comment on the video.
        
        Args:
            comment: Comment text
        """
        try:
            # Scroll down to comments section
            self.human_behavior.scroll_page(direction="down", distance=800)
            time.sleep(random.uniform(2, 3))
            
            # Find comment input
            try:
                comment_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#simplebox-placeholder"))
                )
                
                # Click on comment input
                self.human_behavior.move_to_element(comment_input)
                time.sleep(random.uniform(0.5, 1))
                comment_input.click()
                time.sleep(random.uniform(1, 2))
                
                # Find the actual textarea
                comment_textarea = self.driver.find_element(By.CSS_SELECTOR, "#contenteditable-root")
                
                # Type comment with human-like delays
                self.human_behavior.type_text(comment_textarea, comment)
                time.sleep(random.uniform(1, 2))
                
                # Submit comment
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "#submit-button")
                self.human_behavior.move_to_element(submit_button)
                time.sleep(random.uniform(0.5, 1))
                submit_button.click()
                
                logger.info(f"Commented on video: {comment}")
                
                # Take screenshot
                time.sleep(random.uniform(2, 3))
                self.proof_system.take_screenshot("youtube_comment_proof")
                
            except TimeoutException:
                logger.warning("Comment input not found")
        
        except Exception as e:
            logger.error(f"Error commenting on video: {str(e)}")
    
    def _generate_proof_description(self, task: Dict[str, Any], video_duration: int, actions_performed: List[str]) -> str:
        """
        Generate proof description.
        
        Args:
            task: Task information
            video_duration: Video duration in seconds
            actions_performed: List of actions performed
        
        Returns:
            str: Proof description
        """
        # Format video duration
        minutes = video_duration // 60
        seconds = video_duration % 60
        duration_str = f"{minutes}:{seconds:02d}"
        
        # Base description
        description = f"I watched the entire YouTube video (duration: {duration_str})."
        
        # Add actions performed
        if "like" in actions_performed:
            description += " I liked the video as requested."
        
        if "comment" in actions_performed:
            description += " I also left a comment on the video."
        
        # Add timestamp
        description += f" Completed on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."
        
        return description