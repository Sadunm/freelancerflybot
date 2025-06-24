#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Temporary Email Client Module
--------------------------
Provides functionality for creating and accessing temporary email addresses.
"""

import os
import json
import time
import random
import string
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TempMailClient:
    """Client for temporary email services."""
    
    def __init__(self, api_key: Optional[str] = None, config_file: str = "freelancerfly_bot/config/temp_mail_config.json"):
        """
        Initialize temporary email client.
        
        Args:
            api_key: API key for temp-mail.org (optional)
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
        # Set API key
        self.api_key = api_key or self.config.get("api_key", "")
        
        # Set API endpoints
        self.api_base_url = self.config.get("api_base_url", "https://api.temp-mail.org/request")
        
        # Set domains
        self.domains = self.config.get("domains", [
            "temp-mail.org",
            "temp-mail.io",
            "tempmail.com",
            "tmpmail.net",
            "tmpmail.org",
            "tmpeml.com"
        ])
        
        # Cache for email addresses and messages
        self.email_cache = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration
        """
        default_config = {
            "api_key": "",
            "api_base_url": "https://api.temp-mail.org/request",
            "domains": [
                "temp-mail.org",
                "temp-mail.io",
                "tempmail.com",
                "tmpmail.net",
                "tmpmail.org",
                "tmpeml.com"
            ],
            "check_interval": 10,  # seconds
            "max_check_attempts": 30,  # 5 minutes with 10-second interval
            "use_api": False  # Whether to use the API or generate locally
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.debug(f"Loaded temp mail config from {self.config_file}")
                return config
            else:
                # Create config file with default config
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created temp mail config at {self.config_file}")
                return default_config
        except Exception as e:
            logger.error(f"Error loading temp mail config: {str(e)}")
            return default_config
    
    def get_email(self) -> str:
        """
        Get a temporary email address.
        
        Returns:
            str: Temporary email address
        """
        # Check if we should use the API
        if self.config.get("use_api", False) and self.api_key:
            return self._get_email_api()
        else:
            return self._generate_email_local()
    
    def _get_email_api(self) -> str:
        """
        Get a temporary email address using the API.
        
        Returns:
            str: Temporary email address
        """
        try:
            # Make API request
            response = requests.get(
                f"{self.api_base_url}/email/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                email = data.get("email", "")
                
                if email:
                    logger.info(f"Generated temporary email: {email}")
                    return email
            
            logger.warning(f"Failed to get email from API: {response.status_code} {response.text}")
        
        except Exception as e:
            logger.error(f"Error getting email from API: {str(e)}")
        
        # Fallback to local generation
        return self._generate_email_local()
    
    def _generate_email_local(self) -> str:
        """
        Generate a temporary email address locally.
        
        Returns:
            str: Temporary email address
        """
        # Generate random username
        username_length = random.randint(8, 12)
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
        
        # Choose random domain
        domain = random.choice(self.domains)
        
        # Create email
        email = f"{username}@{domain}"
        
        logger.info(f"Generated temporary email locally: {email}")
        
        return email
    
    def get_emails(self, email: str) -> List[Dict[str, Any]]:
        """
        Get emails for a temporary email address.
        
        Args:
            email: Temporary email address
        
        Returns:
            List[Dict[str, Any]]: List of emails
        """
        # Check if we should use the API
        if self.config.get("use_api", False) and self.api_key:
            return self._get_emails_api(email)
        else:
            return self._get_emails_local(email)
    
    def _get_emails_api(self, email: str) -> List[Dict[str, Any]]:
        """
        Get emails for a temporary email address using the API.
        
        Args:
            email: Temporary email address
        
        Returns:
            List[Dict[str, Any]]: List of emails
        """
        try:
            # Make API request
            response = requests.get(
                f"{self.api_base_url}/email/messages",
                params={"email": email},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                logger.info(f"Got {len(messages)} emails for {email}")
                
                return messages
            
            logger.warning(f"Failed to get emails from API: {response.status_code} {response.text}")
        
        except Exception as e:
            logger.error(f"Error getting emails from API: {str(e)}")
        
        return []
    
    def _get_emails_local(self, email: str) -> List[Dict[str, Any]]:
        """
        Simulate getting emails for a temporary email address locally.
        
        Args:
            email: Temporary email address
        
        Returns:
            List[Dict[str, Any]]: List of emails
        """
        # Check if we have cached emails for this address
        if email in self.email_cache:
            return self.email_cache[email]
        
        # Simulate no emails initially
        self.email_cache[email] = []
        
        # Simulate receiving an email after a delay
        # This is just a placeholder for testing
        # In a real implementation, we would need to periodically check for new emails
        
        return []
    
    def wait_for_email(self, email: str, subject_contains: Optional[str] = None, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """
        Wait for an email to arrive.
        
        Args:
            email: Temporary email address
            subject_contains: Text that should be in the subject (optional)
            timeout: Timeout in seconds
        
        Returns:
            Optional[Dict[str, Any]]: Email, or None if timeout
        """
        logger.info(f"Waiting for email to {email}" + (f" with subject containing '{subject_contains}'" if subject_contains else ""))
        
        # Calculate check interval and max attempts
        check_interval = self.config.get("check_interval", 10)  # seconds
        max_attempts = timeout // check_interval
        
        # Check for emails
        for attempt in range(max_attempts):
            # Get emails
            emails = self.get_emails(email)
            
            # Filter by subject if needed
            if subject_contains:
                filtered_emails = [e for e in emails if subject_contains.lower() in e.get("subject", "").lower()]
            else:
                filtered_emails = emails
            
            # Return first matching email
            if filtered_emails:
                logger.info(f"Found matching email after {attempt * check_interval} seconds")
                return filtered_emails[0]
            
            # Wait before next check
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for email to {email}")
        return None
    
    def get_email_content(self, email: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content of a specific email.
        
        Args:
            email: Temporary email address
            message_id: Message ID
        
        Returns:
            Optional[Dict[str, Any]]: Email content, or None if not found
        """
        # Check if we should use the API
        if self.config.get("use_api", False) and self.api_key:
            return self._get_email_content_api(email, message_id)
        else:
            return self._get_email_content_local(email, message_id)
    
    def _get_email_content_api(self, email: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content of a specific email using the API.
        
        Args:
            email: Temporary email address
            message_id: Message ID
        
        Returns:
            Optional[Dict[str, Any]]: Email content, or None if not found
        """
        try:
            # Make API request
            response = requests.get(
                f"{self.api_base_url}/email/message/{message_id}",
                params={"email": email},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"Got email content for message {message_id}")
                
                return data
            
            logger.warning(f"Failed to get email content from API: {response.status_code} {response.text}")
        
        except Exception as e:
            logger.error(f"Error getting email content from API: {str(e)}")
        
        return None
    
    def _get_email_content_local(self, email: str, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Simulate getting content of a specific email locally.
        
        Args:
            email: Temporary email address
            message_id: Message ID
        
        Returns:
            Optional[Dict[str, Any]]: Email content, or None if not found
        """
        # Check if we have cached emails for this address
        if email in self.email_cache:
            # Find email with matching ID
            for message in self.email_cache[email]:
                if message.get("id") == message_id:
                    return message
        
        return None
    
    def extract_verification_link(self, email_content: Dict[str, Any]) -> Optional[str]:
        """
        Extract verification link from email content.
        
        Args:
            email_content: Email content
        
        Returns:
            Optional[str]: Verification link, or None if not found
        """
        # Get email body
        body = email_content.get("body", "")
        
        # Look for common verification link patterns
        patterns = [
            r'https?://[^\s<>"\']+/verify[^\s<>"\']*',
            r'https?://[^\s<>"\']+/confirm[^\s<>"\']*',
            r'https?://[^\s<>"\']+/activate[^\s<>"\']*',
            r'https?://[^\s<>"\']+/validation[^\s<>"\']*',
            r'https?://[^\s<>"\']+token=[^\s<>"\']*'
        ]
        
        import re
        
        # Try each pattern
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                link = match.group(0)
                logger.info(f"Extracted verification link: {link}")
                return link
        
        logger.warning("No verification link found in email")
        return None
    
    def simulate_email_verification(self, email: str) -> Dict[str, Any]:
        """
        Simulate email verification for testing.
        
        Args:
            email: Temporary email address
        
        Returns:
            Dict[str, Any]: Simulated verification email
        """
        # Generate a random verification link
        verification_link = f"https://example.com/verify?token={''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
        
        # Create a simulated verification email
        verification_email = {
            "id": f"msg_{int(time.time())}_{random.randint(1000, 9999)}",
            "from": "noreply@example.com",
            "to": email,
            "subject": "Verify Your Email Address",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "body": f"""
                <html>
                <body>
                    <p>Thank you for signing up!</p>
                    <p>Please click the link below to verify your email address:</p>
                    <p><a href="{verification_link}">{verification_link}</a></p>
                    <p>If you did not sign up for this service, please ignore this email.</p>
                </body>
                </html>
            """,
            "text_body": f"""
                Thank you for signing up!
                
                Please click the link below to verify your email address:
                {verification_link}
                
                If you did not sign up for this service, please ignore this email.
            """,
            "verification_link": verification_link
        }
        
        # Add to cache
        if email not in self.email_cache:
            self.email_cache[email] = []
        
        self.email_cache[email].append(verification_email)
        
        logger.info(f"Simulated verification email for {email}")
        
        return verification_email