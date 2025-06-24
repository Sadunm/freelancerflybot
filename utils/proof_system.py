#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Proof System Module
-----------------
Handles proof generation for tasks, including screenshots, screen recording, and OCR.
"""

import os
import time
import random
import logging
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)

class ProofSystem:
    """Handles proof generation for tasks."""
    
    def __init__(self, driver, account_email: str, session_id: Optional[str] = None):
        """
        Initialize proof system.
        
        Args:
            driver: Selenium WebDriver instance
            account_email: Account email
            session_id: Current session identifier
        """
        self.driver = driver
        self.account_email = account_email
        self.session_id = session_id
        
        # Create safe account name for file paths
        self.safe_account = account_email.replace('@', '_at_').replace('.', '_dot_')
        
        # Create proof directory
        self.proof_dir = os.path.join("freelancerfly_bot", "proofs", self.safe_account)
        if session_id:
            self.proof_dir = os.path.join(self.proof_dir, session_id)
        
        os.makedirs(self.proof_dir, exist_ok=True)
    
    def take_screenshot(self, name: str) -> str:
        """
        Take a screenshot.
        
        Args:
            name: Screenshot name
        
        Returns:
            str: Path to screenshot
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(self.proof_dir, filename)
            
            # Take screenshot
            self.driver.save_screenshot(filepath)
            
            # Add watermark
            self._add_watermark(filepath)
            
            logger.debug(f"Took screenshot: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return ""
    
    def record_screen(self, name: str, duration: int = 10) -> str:
        """
        Record screen for a specified duration.
        
        Args:
            name: Recording name
            duration: Recording duration in seconds
        
        Returns:
            str: Path to recording
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.webm"
            filepath = os.path.join(self.proof_dir, filename)
            
            # Take screenshot first (as fallback)
            screenshot_path = self.take_screenshot(f"{name}_screenshot")
            
            # Check if ffmpeg is available
            try:
                # Create temporary directory for frames
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Take screenshots for frames
                    frame_paths = []
                    
                    for i in range(duration):
                        # Take screenshot
                        frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                        self.driver.save_screenshot(frame_path)
                        frame_paths.append(frame_path)
                        
                        # Add watermark
                        self._add_watermark(frame_path)
                        
                        # Wait for next frame
                        time.sleep(1)
                    
                    # Create video from frames
                    ffmpeg_cmd = [
                        "ffmpeg",
                        "-y",  # Overwrite output file if it exists
                        "-framerate", "1",  # 1 frame per second
                        "-i", os.path.join(temp_dir, "frame_%04d.png"),
                        "-c:v", "libvpx-vp9",
                        "-crf", "30",
                        "-b:v", "500k",
                        filepath
                    ]
                    
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    logger.info(f"Recorded screen: {filepath}")
                    
                    return filepath
            
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.warning(f"Error recording screen with ffmpeg: {str(e)}")
                logger.warning("Falling back to screenshot")
                return screenshot_path
        
        except Exception as e:
            logger.error(f"Error recording screen: {str(e)}")
            return ""
    
    def _add_watermark(self, image_path: str):
        """
        Add watermark to image.
        
        Args:
            image_path: Path to image
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Create draw object
            draw = ImageDraw.Draw(image)
            
            # Get image dimensions
            width, height = image.size
            
            # Create watermark text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            watermark_text = f"FreelancerFly Bot - {self.account_email} - {timestamp}"
            
            # Set font
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except IOError:
                font = ImageFont.load_default()
            
            # Calculate text size
            text_width, text_height = draw.textsize(watermark_text, font=font)
            
            # Calculate position (bottom right)
            x = width - text_width - 10
            y = height - text_height - 10
            
            # Draw semi-transparent background
            draw.rectangle([(x - 5, y - 5), (x + text_width + 5, y + text_height + 5)], fill=(0, 0, 0, 128))
            
            # Draw text
            draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
            
            # Save image
            image.save(image_path)
        
        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
    
    def highlight_element(self, element, name: str) -> str:
        """
        Take a screenshot with an element highlighted.
        
        Args:
            element: Element to highlight
            name: Screenshot name
        
        Returns:
            str: Path to screenshot
        """
        try:
            # Take screenshot
            screenshot_path = self.take_screenshot(name)
            
            # Get element location and size
            location = element.location
            size = element.size
            
            # Open image
            image = Image.open(screenshot_path)
            
            # Create draw object
            draw = ImageDraw.Draw(image)
            
            # Calculate element coordinates
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            
            # Draw rectangle around element
            draw.rectangle([(left, top), (right, bottom)], outline=(255, 0, 0), width=3)
            
            # Save image
            image.save(screenshot_path)
            
            logger.debug(f"Highlighted element in screenshot: {screenshot_path}")
            
            return screenshot_path
        
        except Exception as e:
            logger.error(f"Error highlighting element: {str(e)}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image
        
        Returns:
            str: Extracted text
        """
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract OCR not available")
            return ""
        
        try:
            # Open image
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            logger.debug(f"Extracted text from image: {image_path}")
            
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def verify_text_in_image(self, image_path: str, text: str) -> bool:
        """
        Verify if text is present in image.
        
        Args:
            image_path: Path to image
            text: Text to verify
        
        Returns:
            bool: True if text is present, False otherwise
        """
        extracted_text = self.extract_text_from_image(image_path)
        
        return text.lower() in extracted_text.lower()
    
    def compare_images(self, image1_path: str, image2_path: str) -> float:
        """
        Compare two images and return similarity score.
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
        
        Returns:
            float: Similarity score (0-1)
        """
        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            # Resize images to same size
            img1 = cv2.resize(img1, (500, 500))
            img2 = cv2.resize(img2, (500, 500))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity index
            (score, diff) = cv2.compareSSIM(gray1, gray2, full=True)
            
            logger.debug(f"Image similarity score: {score}")
            
            return score
        
        except Exception as e:
            logger.error(f"Error comparing images: {str(e)}")
            return 0.0