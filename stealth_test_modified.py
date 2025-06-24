#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Stealth Test Script for FreelancerFly Bot.
Tests the anti-detection measures by visiting bot detection websites.
"""

import os
import time
import json
import logging
import argparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Use relative imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.browser_manager import BrowserManager
from utils.stealth import apply_stealth_settings
from utils.fingerprint import generate_fingerprint_overrides
from utils.logger import setup_logger
from utils.human_behavior import HumanBehavior

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FreelancerFly Bot Stealth Test')
    parser.add_argument('--headless', action='store_true',
                        help='Run in headless mode')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level')
    return parser.parse_args()

def run_stealth_test(args):
    """Run stealth test."""
    # Setup logging
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = setup_logger(
        log_file=f"logs/stealth_test_{session_id}.log",
        level=getattr(logging, args.log_level)
    )
    
    logger.info("Starting FreelancerFly Bot Stealth Test")
    
    # Initialize browser manager
    browser_manager = BrowserManager(
        headless=args.headless,
        session_id=session_id
    )
    
    # Get driver
    driver = browser_manager.get_driver()
    
    # Initialize human behavior
    human_behavior = HumanBehavior(driver)
    
    # Test sites
    test_sites = [
        {
            "name": "Cloudflare Browser Challenge",
            "url": "https://www.cloudflare.com/",
            "success_indicator": "title:Cloudflare",
            "failure_indicator": "title:Attention Required"
        },
        {
            "name": "Bot Detection Test",
            "url": "https://bot.sannysoft.com/",
            "success_indicator": "text:WebDriver",
            "failure_indicator": None
        },
        {
            "name": "Browser Leaks",
            "url": "https://browserleaks.com/javascript",
            "success_indicator": "title:JavaScript",
            "failure_indicator": None
        },
        {
            "name": "Canvas Fingerprint Test",
            "url": "https://browserleaks.com/canvas",
            "success_indicator": "title:Canvas",
            "failure_indicator": None
        },
        {
            "name": "WebGL Fingerprint Test",
            "url": "https://browserleaks.com/webgl",
            "success_indicator": "title:WebGL",
            "failure_indicator": None
        },
        {
            "name": "Audio Fingerprint Test",
            "url": "https://audiofingerprint.openwpm.com/",
            "success_indicator": "title:Audio Fingerprinting",
            "failure_indicator": None
        },
        {
            "name": "Recaptcha Test",
            "url": "https://www.google.com/recaptcha/api2/demo",
            "success_indicator": "title:reCAPTCHA",
            "failure_indicator": None
        }
    ]
    
    # Results
    results = {
        "timestamp": datetime.now().isoformat(),
        "headless": args.headless,
        "tests": []
    }
    
    try:
        # Run tests
        for test in test_sites:
            logger.info(f"Testing {test['name']} ({test['url']})")
            
            test_result = {
                "name": test["name"],
                "url": test["url"],
                "success": False,
                "details": {},
                "screenshot": None
            }
            
            try:
                # Navigate to site
                driver.get(test["url"])
                
                # Wait for page to load
                time.sleep(5)
                
                # Simulate human behavior
                human_behavior.scroll_page(direction="down", distance=300)
                time.sleep(1)
                human_behavior.move_mouse_randomly()
                time.sleep(1)
                human_behavior.scroll_page(direction="up", distance=100)
                
                # Take screenshot
                screenshot_path = f"logs/stealth_test_{test['name'].replace(' ', '_').lower()}_{session_id}.png"
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                driver.save_screenshot(screenshot_path)
                test_result["screenshot"] = screenshot_path
                
                # Check success indicator
                if test["success_indicator"]:
                    indicator_type, indicator_value = test["success_indicator"].split(":", 1)
                    
                    if indicator_type == "title":
                        test_result["success"] = indicator_value in driver.title
                        test_result["details"]["title"] = driver.title
                    elif indicator_type == "text":
                        test_result["success"] = indicator_value in driver.page_source
                        test_result["details"]["text_found"] = indicator_value in driver.page_source
                
                # Check failure indicator
                if test["failure_indicator"]:
                    indicator_type, indicator_value = test["failure_indicator"].split(":", 1)
                    
                    if indicator_type == "title":
                        test_result["success"] = indicator_value not in driver.title
                        test_result["details"]["title"] = driver.title
                    elif indicator_type == "text":
                        test_result["success"] = indicator_value not in driver.page_source
                        test_result["details"]["text_found"] = indicator_value not in driver.page_source
                
                # Collect additional details
                if test["name"] == "Bot Detection Test":
                    # Check WebDriver detection
                    webdriver_results = driver.find_elements(By.CSS_SELECTOR, ".webdriver-result")
                    for result in webdriver_results:
                        name_element = result.find_element(By.CSS_SELECTOR, ".name")
                        value_element = result.find_element(By.CSS_SELECTOR, ".value")
                        
                        name = name_element.text.strip()
                        value = value_element.text.strip()
                        
                        test_result["details"][name] = value
                        
                        # Check if any test failed
                        if "FAIL" in value:
                            test_result["success"] = False
                
                logger.info(f"Test result: {'Success' if test_result['success'] else 'Failure'}")
            
            except Exception as e:
                logger.error(f"Error testing {test['name']}: {str(e)}")
                test_result["success"] = False
                test_result["details"]["error"] = str(e)
            
            # Add test result
            results["tests"].append(test_result)
            
            # Wait between tests
            time.sleep(3)
    
    except Exception as e:
        logger.error(f"Error running stealth test: {str(e)}")
    finally:
        # Quit browser
        browser_manager.quit()
        
        # Save results
        results_file = f"logs/stealth_test_results_{session_id}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("FreelancerFly Bot Stealth Test Summary")
        print("="*50)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Headless mode: {results['headless']}")
        print("\nTest results:")
        
        success_count = 0
        for test in results["tests"]:
            status = "[PASS]" if test["success"] else "[FAIL]"
            print(f"  {status} - {test['name']}")
            if test["screenshot"]:
                print(f"    Screenshot: {test['screenshot']}")
            
            if test["success"]:
                success_count += 1
        
        success_rate = (success_count / len(results["tests"])) * 100 if results["tests"] else 0
        print(f"\nSuccess rate: {success_rate:.1f}% ({success_count}/{len(results['tests'])})")
        print("\nDetailed results saved to:", results_file)
        print("="*50)

if __name__ == "__main__":
    args = parse_arguments()
    run_stealth_test(args)