#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Signup Task Executor Module
-------------------------
Executes signup-related tasks such as creating accounts on websites.
"""

import re
import time
import random
import logging
import json
import os
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from freelancerfly_bot.utils.human_behavior import HumanBehavior
from freelancerfly_bot.utils.temp_mail import TempMailClient
from freelancerfly_bot.utils.fake_data import FakeDataGenerator

logger = logging.getLogger(__name__)

class SignupTaskExecutor:
    """Executes signup-related tasks."""
    
    def __init__(self, driver, proof_system):
        """
        Initialize signup task executor.
        
        Args:
            driver: Selenium WebDriver instance
            proof_system: Proof system instance
        """
        self.driver = driver
        self.proof_system = proof_system
        self.human_behavior = HumanBehavior(driver)
        self.temp_mail = TempMailClient()
        self.fake_data = FakeDataGenerator()
        
        # Load config
        self.config_file = "freelancerfly_bot/config/signup_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load signup configuration.
        
        Returns:
            Dict[str, Any]: Signup configuration
        """
        default_config = {
            "max_wait_time": 300,  # Maximum time to wait for email verification (seconds)
            "temp_mail_api_key": "",  # TempMail API key
            "blacklisted_domains": [
                "facebook.com",
                "twitter.com",
                "instagram.com",
                "tiktok.com",
                "snapchat.com",
                "linkedin.com"
            ],
            "form_field_mappings": {
                "email": ["email", "e-mail", "mail"],
                "password": ["password", "pass", "pwd"],
                "username": ["username", "user", "login", "nickname"],
                "first_name": ["first name", "firstname", "fname", "given name"],
                "last_name": ["last name", "lastname", "lname", "surname", "family name"],
                "full_name": ["full name", "name", "your name"],
                "phone": ["phone", "mobile", "cell", "telephone"],
                "address": ["address", "street", "addr"],
                "city": ["city", "town"],
                "state": ["state", "province", "region"],
                "zip": ["zip", "postal", "postcode", "zip code"],
                "country": ["country", "nation"],
                "birthday": ["birthday", "birth date", "date of birth", "dob"],
                "gender": ["gender", "sex"]
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.debug(f"Loaded signup config from {self.config_file}")
                return config
            else:
                # Create config file with default config
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created signup config at {self.config_file}")
                return default_config
        except Exception as e:
            logger.error(f"Error loading signup config: {str(e)}")
            return default_config
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a signup task.
        
        Args:
            task: Task information
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        task_id = task["id"]
        
        try:
            # Extract signup URL from task
            signup_url = self._extract_signup_url(task)
            if not signup_url:
                logger.warning(f"No signup URL found in task {task_id}")
                return {
                    "success": False,
                    "error": "No signup URL found in task"
                }
            
            # Check if domain is blacklisted
            domain = self._extract_domain(signup_url)
            if domain in self.config.get("blacklisted_domains", []):
                logger.warning(f"Domain {domain} is blacklisted")
                return {
                    "success": False,
                    "error": f"Domain {domain} is blacklisted"
                }
            
            logger.info(f"Executing signup task: {signup_url}")
            
            # Navigate to signup URL
            self.driver.get(signup_url)
            time.sleep(random.uniform(3, 5))
            
            # Take screenshot of initial state
            initial_screenshot = self.proof_system.take_screenshot(f"signup_{task_id}_initial")
            
            # Find signup form
            form = self._find_signup_form()
            if not form:
                logger.warning(f"Signup form not found on {signup_url}")
                return {
                    "success": False,
                    "error": "Signup form not found"
                }
            
            # Generate fake data for signup
            fake_data = self._generate_fake_data()
            
            # Fill signup form
            form_data = self._fill_signup_form(form, fake_data)
            if not form_data["success"]:
                return form_data
            
            # Take screenshot of filled form
            filled_form_screenshot = self.proof_system.take_screenshot(f"signup_{task_id}_filled_form")
            
            # Submit form
            submit_result = self._submit_form(form)
            if not submit_result["success"]:
                return submit_result
            
            # Take screenshot after submission
            submission_screenshot = self.proof_system.take_screenshot(f"signup_{task_id}_submission")
            
            # Check for email verification
            if form_data.get("requires_email_verification", False):
                verification_result = self._handle_email_verification(fake_data["email"])
                if not verification_result["success"]:
                    # Even if verification fails, we consider the task partially successful
                    logger.warning(f"Email verification failed: {verification_result['error']}")
            
            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"signup_{task_id}_final")
            
            # Generate proof description
            description = self._generate_proof_description(task, fake_data, form_data)
            
            return {
                "success": True,
                "proof": {
                    "description": description,
                    "screenshots": [initial_screenshot, filled_form_screenshot, submission_screenshot, final_screenshot]
                }
            }
        
        except Exception as e:
            logger.error(f"Error executing signup task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_signup_url(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Extract signup URL from task.
        
        Args:
            task: Task information
        
        Returns:
            Optional[str]: Signup URL, or None if not found
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
                    if any(keyword in link_text for keyword in ["sign up", "register", "create account", "join"]):
                        return href
        except Exception:
            pass
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL
        
        Returns:
            str: Domain
        """
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1)
        return ""
    
    def _find_signup_form(self) -> Optional[Any]:
        """
        Find signup form on the page.
        
        Returns:
            Optional[Any]: Signup form element, or None if not found
        """
        # Try to find form by common attributes
        form_selectors = [
            "form[id*='signup']",
            "form[id*='register']",
            "form[class*='signup']",
            "form[class*='register']",
            "form[action*='signup']",
            "form[action*='register']",
            "form[name*='signup']",
            "form[name*='register']",
            "form"  # Fallback to any form
        ]
        
        for selector in form_selectors:
            forms = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if forms:
                # Try to find the most likely signup form
                for form in forms:
                    # Check if form has email and password fields
                    email_field = self._find_field(form, "email")
                    password_field = self._find_field(form, "password")
                    
                    if email_field and password_field:
                        return form
                
                # If no form with email and password found, return the first form
                return forms[0]
        
        return None
    
    def _find_field(self, form, field_type: str) -> Optional[Any]:
        """
        Find a field in a form.
        
        Args:
            form: Form element
            field_type: Field type (e.g., "email", "password")
        
        Returns:
            Optional[Any]: Field element, or None if not found
        """
        field_mappings = self.config.get("form_field_mappings", {})
        field_keywords = field_mappings.get(field_type, [field_type])
        
        # Try to find by input type
        if field_type in ["email", "password"]:
            fields = form.find_elements(By.CSS_SELECTOR, f"input[type='{field_type}']")
            if fields:
                return fields[0]
        
        # Try to find by name, id, placeholder, or label
        for keyword in field_keywords:
            # Try by name
            fields = form.find_elements(By.CSS_SELECTOR, f"input[name*='{keyword}' i]")
            if fields:
                return fields[0]
            
            # Try by id
            fields = form.find_elements(By.CSS_SELECTOR, f"input[id*='{keyword}' i]")
            if fields:
                return fields[0]
            
            # Try by placeholder
            fields = form.find_elements(By.CSS_SELECTOR, f"input[placeholder*='{keyword}' i]")
            if fields:
                return fields[0]
            
            # Try by aria-label
            fields = form.find_elements(By.CSS_SELECTOR, f"input[aria-label*='{keyword}' i]")
            if fields:
                return fields[0]
            
            # Try by label
            labels = form.find_elements(By.XPATH, f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            for label in labels:
                for_attr = label.get_attribute("for")
                if for_attr:
                    field = form.find_elements(By.CSS_SELECTOR, f"input[id='{for_attr}']")
                    if field:
                        return field[0]
        
        return None
    
    def _generate_fake_data(self) -> Dict[str, Any]:
        """
        Generate fake data for signup.
        
        Returns:
            Dict[str, Any]: Fake data
        """
        # Generate temporary email
        email = self.temp_mail.get_email()
        
        # Generate other fake data
        fake_data = {
            "email": email,
            "password": self.fake_data.generate_password(),
            "username": self.fake_data.generate_username(),
            "first_name": self.fake_data.generate_first_name(),
            "last_name": self.fake_data.generate_last_name(),
            "phone": self.fake_data.generate_phone(),
            "address": self.fake_data.generate_address(),
            "city": self.fake_data.generate_city(),
            "state": self.fake_data.generate_state(),
            "zip": self.fake_data.generate_zip(),
            "country": self.fake_data.generate_country(),
            "birthday": self.fake_data.generate_birthday(),
            "gender": self.fake_data.generate_gender()
        }
        
        # Add full name
        fake_data["full_name"] = f"{fake_data['first_name']} {fake_data['last_name']}"
        
        logger.debug(f"Generated fake data: {fake_data['email']}, {fake_data['username']}")
        
        return fake_data
    
    def _fill_signup_form(self, form, fake_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fill signup form with fake data.
        
        Args:
            form: Form element
            fake_data: Fake data
        
        Returns:
            Dict[str, Any]: Form filling result
        """
        try:
            filled_fields = []
            requires_email_verification = False
            
            # Try to fill common fields
            field_types = [
                "email", "password", "username", "first_name", "last_name",
                "full_name", "phone", "address", "city", "state", "zip",
                "country", "birthday", "gender"
            ]
            
            for field_type in field_types:
                field = self._find_field(form, field_type)
                if field:
                    # Get field value
                    value = fake_data.get(field_type, "")
                    
                    # Fill field
                    self.human_behavior.move_to_element(field)
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    # Clear field if needed
                    field.clear()
                    time.sleep(random.uniform(0.2, 0.5))
                    
                    # Type value with human-like delays
                    self.human_behavior.type_text(field, value)
                    
                    filled_fields.append(field_type)
                    
                    # If email field is filled, we might need email verification
                    if field_type == "email":
                        requires_email_verification = True
            
            # Check for checkboxes (terms, privacy policy, etc.)
            checkboxes = form.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            for checkbox in checkboxes:
                # Check if it's a required checkbox
                required = checkbox.get_attribute("required") == "true"
                
                # Check if it's likely a terms checkbox
                checkbox_id = checkbox.get_attribute("id") or ""
                checkbox_name = checkbox.get_attribute("name") or ""
                checkbox_label_text = ""
                
                # Try to find associated label
                if checkbox_id:
                    label = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                    if label:
                        checkbox_label_text = label[0].text.lower()
                
                # Check if it's a terms checkbox
                is_terms_checkbox = any(keyword in (checkbox_id + checkbox_name + checkbox_label_text).lower() 
                                        for keyword in ["terms", "privacy", "agree", "consent", "accept"])
                
                # Check the checkbox if required or if it's a terms checkbox
                if required or is_terms_checkbox:
                    if not checkbox.is_selected():
                        self.human_behavior.move_to_element(checkbox)
                        time.sleep(random.uniform(0.3, 0.7))
                        checkbox.click()
                        time.sleep(random.uniform(0.2, 0.5))
                        filled_fields.append("checkbox")
            
            # Check for CAPTCHA
            captcha_detected = self._detect_captcha()
            
            logger.info(f"Filled form fields: {', '.join(filled_fields)}")
            
            return {
                "success": True,
                "filled_fields": filled_fields,
                "requires_email_verification": requires_email_verification,
                "captcha_detected": captcha_detected
            }
        
        except Exception as e:
            logger.error(f"Error filling signup form: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _detect_captcha(self) -> bool:
        """
        Detect if there's a CAPTCHA on the page.
        
        Returns:
            bool: True if CAPTCHA detected, False otherwise
        """
        # Check for common CAPTCHA elements
        captcha_indicators = [
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            "div[class*='recaptcha']",
            "div[class*='captcha']",
            "input[name*='captcha']",
            "img[src*='captcha']"
        ]
        
        for indicator in captcha_indicators:
            elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
            if elements:
                logger.warning("CAPTCHA detected on the page")
                return True
        
        return False
    
    def _submit_form(self, form) -> Dict[str, Any]:
        """
        Submit the form.
        
        Args:
            form: Form element
        
        Returns:
            Dict[str, Any]: Form submission result
        """
        try:
            # Find submit button
            submit_button = self._find_submit_button(form)
            if not submit_button:
                logger.warning("Submit button not found")
                return {
                    "success": False,
                    "error": "Submit button not found"
                }
            
            # Click submit button
            self.human_behavior.move_to_element(submit_button)
            time.sleep(random.uniform(0.5, 1))
            submit_button.click()
            
            logger.info("Submitted signup form")
            
            # Wait for page to load
            time.sleep(random.uniform(3, 5))
            
            # Check for errors
            error_messages = self._check_for_errors()
            if error_messages:
                logger.warning(f"Signup errors detected: {error_messages}")
                return {
                    "success": False,
                    "error": error_messages
                }
            
            return {"success": True}
        
        except Exception as e:
            logger.error(f"Error submitting form: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _find_submit_button(self, form) -> Optional[Any]:
        """
        Find submit button in a form.
        
        Args:
            form: Form element
        
        Returns:
            Optional[Any]: Submit button element, or None if not found
        """
        # Try to find by type
        buttons = form.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        if buttons:
            return buttons[0]
        
        # Try to find by text
        submit_keywords = ["sign up", "register", "create account", "join", "submit", "continue"]
        for keyword in submit_keywords:
            buttons = form.find_elements(By.XPATH, f".//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if buttons:
                return buttons[0]
        
        # Try to find by class or id
        button_selectors = [
            "button[class*='submit']",
            "button[class*='signup']",
            "button[class*='register']",
            "button[id*='submit']",
            "button[id*='signup']",
            "button[id*='register']",
            "button"  # Fallback to any button
        ]
        
        for selector in button_selectors:
            buttons = form.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                return buttons[0]
        
        return None
    
    def _check_for_errors(self) -> str:
        """
        Check for error messages on the page.
        
        Returns:
            str: Error messages, or empty string if none found
        """
        # Common error selectors
        error_selectors = [
            ".error",
            ".alert-danger",
            ".alert-error",
            ".form-error",
            ".validation-error",
            "[class*='error']",
            "[class*='alert']"
        ]
        
        error_messages = []
        
        for selector in error_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = element.text.strip()
                if text and len(text) > 3:  # Ignore very short texts
                    error_messages.append(text)
        
        return ", ".join(error_messages)
    
    def _handle_email_verification(self, email: str) -> Dict[str, Any]:
        """
        Handle email verification.
        
        Args:
            email: Email address
        
        Returns:
            Dict[str, Any]: Verification result
        """
        try:
            logger.info(f"Waiting for verification email for {email}")
            
            # Maximum wait time
            max_wait_time = self.config.get("max_wait_time", 300)  # 5 minutes
            start_time = time.time()
            
            # Check for emails
            while time.time() - start_time < max_wait_time:
                # Get emails
                emails = self.temp_mail.get_emails(email)
                
                if emails:
                    # Process the most recent email
                    latest_email = emails[0]
                    
                    # Take screenshot of email
                    self.proof_system.take_screenshot("email_verification")
                    
                    # Extract verification link
                    verification_link = self._extract_verification_link(latest_email)
                    
                    if verification_link:
                        # Navigate to verification link
                        self.driver.get(verification_link)
                        time.sleep(random.uniform(3, 5))
                        
                        # Take screenshot of verification page
                        self.proof_system.take_screenshot("email_verification_completed")
                        
                        logger.info(f"Completed email verification for {email}")
                        return {"success": True}
                    else:
                        logger.warning(f"No verification link found in email for {email}")
                        return {
                            "success": False,
                            "error": "No verification link found in email"
                        }
                
                # Wait before checking again
                time.sleep(10)
            
            logger.warning(f"Timeout waiting for verification email for {email}")
            return {
                "success": False,
                "error": "Timeout waiting for verification email"
            }
        
        except Exception as e:
            logger.error(f"Error handling email verification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_verification_link(self, email: Dict[str, Any]) -> Optional[str]:
        """
        Extract verification link from email.
        
        Args:
            email: Email data
        
        Returns:
            Optional[str]: Verification link, or None if not found
        """
        # Get email body
        body = email.get("body", "")
        
        # Try to find verification link
        url_pattern = r'https?://[^\s<>"\'()]+'
        
        # Find all URLs
        urls = re.findall(url_pattern, body)
        
        # Filter URLs that are likely verification links
        verification_keywords = ["verify", "confirm", "activate", "validation"]
        
        for url in urls:
            if any(keyword in url.lower() for keyword in verification_keywords):
                return url
        
        # If no specific verification link found, return the first URL
        if urls:
            return urls[0]
        
        return None
    
    def _generate_proof_description(self, task: Dict[str, Any], fake_data: Dict[str, Any], form_data: Dict[str, Any]) -> str:
        """
        Generate proof description.
        
        Args:
            task: Task information
            fake_data: Fake data used for signup
            form_data: Form data
        
        Returns:
            str: Proof description
        """
        # Get domain
        url = self._extract_signup_url(task)
        domain = self._extract_domain(url)
        
        # Base description
        description = f"I completed the signup process on {domain}."
        
        # Add details about filled fields
        filled_fields = form_data.get("filled_fields", [])
        if filled_fields:
            description += f" I filled out the registration form with the following information: "
            
            field_descriptions = []
            
            if "email" in filled_fields:
                field_descriptions.append(f"email ({fake_data['email']})")
            
            if "username" in filled_fields:
                field_descriptions.append(f"username ({fake_data['username']})")
            
            if "password" in filled_fields:
                field_descriptions.append("password")
            
            if "first_name" in filled_fields or "last_name" in filled_fields or "full_name" in filled_fields:
                field_descriptions.append(f"name ({fake_data['first_name']} {fake_data['last_name']})")
            
            if "phone" in filled_fields:
                field_descriptions.append("phone number")
            
            if "address" in filled_fields or "city" in filled_fields or "state" in filled_fields or "zip" in filled_fields:
                field_descriptions.append("address information")
            
            if "checkbox" in filled_fields:
                field_descriptions.append("required checkboxes")
            
            description += ", ".join(field_descriptions) + "."
        
        # Add email verification info
        if form_data.get("requires_email_verification", False):
            description += f" The temporary email {fake_data['email']} was used for registration."
        
        # Add CAPTCHA info
        if form_data.get("captcha_detected", False):
            description += " CAPTCHA was detected on the page."
        
        # Add timestamp
        description += f" Completed on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}."
        
        return description