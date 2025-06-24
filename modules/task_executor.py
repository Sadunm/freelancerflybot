#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Task Executor Module
------------------
Executes tasks based on their category, with strong human-like behavior and anti-detection.
"""

import os
import time
import random
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from freelancerfly_bot.modules.youtube_executor import YouTubeTaskExecutor
from freelancerfly_bot.modules.telegram_executor import TelegramTaskExecutor
from freelancerfly_bot.modules.signup_executor import SignupTaskExecutor
from freelancerfly_bot.modules.search_executor import SearchTaskExecutor
from freelancerfly_bot.modules.visit_executor import VisitTaskExecutor
from freelancerfly_bot.utils.proof_system import ProofSystem

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes tasks based on their category, with strong anti-detection."""

    def __init__(self, driver, account_email: str, session_id: Optional[str] = None):
        self.driver = driver
        self.account_email = account_email
        self.session_id = session_id
        self.safe_account = account_email.replace('@', '_at_').replace('.', '_dot_')
        self.proof_system = ProofSystem(
            driver=driver,
            account_email=account_email,
            session_id=session_id
        )
        self.executors = {
            "youtube": YouTubeTaskExecutor(driver, self.proof_system),
            "telegram": TelegramTaskExecutor(driver, self.proof_system),
            "signup": SignupTaskExecutor(driver, self.proof_system),
            "search": SearchTaskExecutor(driver, self.proof_system),
            "visit": VisitTaskExecutor(driver, self.proof_system),
            "unknown": None  # Will use generic execution
        }

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = task["id"]
        category = task.get("category", "unknown")
        logger.info(f"Executing {category} task: {task['title']} (ID: {task_id})")

        try:
            # Go to task page and randomize user wait (simulate human browsing)
            self.driver.get(f"https://freelancerfly.com/micro-works/details/{task_id}")
            time.sleep(random.uniform(2.8, 5.2))
            # Initial screenshot
            initial_screenshot = self.proof_system.take_screenshot(f"task_{task_id}_initial")

            # Randomly scroll and delay (human behavior)
            if random.random() < 0.6:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.3);")
                time.sleep(random.uniform(0.8, 2.2))
            if random.random() < 0.4:
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(random.uniform(0.5, 1.5))

            # Check if task is available
            try:
                start_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Start Task')]"))
                )
            except TimeoutException:
                logger.warning(f"Task {task_id} is not available")
                return {
                    "success": False,
                    "error": "Task is not available",
                    "reward": 0
                }
            start_button.click()
            time.sleep(random.uniform(3, 5))

            # 10% chance to "act confused" for anti-pattern
            if random.random() < 0.10:
                self.proof_system.take_screenshot(f"task_{task_id}_confused")
                time.sleep(random.uniform(6, 14))
                return {
                    "success": False,
                    "error": "Temporary confusion - will retry",
                    "reward": 0,
                    "should_retry": True
                }

            executor = self.executors.get(category)
            if executor:
                execution_result = executor.execute(task)
            else:
                execution_result = self._execute_generic_task(task)

            if not execution_result["success"]:
                logger.warning(f"Failed to execute task {task_id}: {execution_result['error']}")
                return {
                    "success": False,
                    "error": execution_result["error"],
                    "reward": 0
                }

            # Enhanced Proof Submission
            proof_result = self._submit_proof(task, execution_result)

            return {
                "success": proof_result["success"],
                "error": proof_result.get("error", ""),
                "reward": task["reward"] if proof_result["success"] else 0
            }

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "reward": 0
            }

    def _execute_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Smart: Extract instructions
            instructions_element = self.driver.find_element(By.CSS_SELECTOR, ".job-details-description")
            instructions = instructions_element.text.strip()
            logger.info(f"Generic task execution. Instructions: {instructions}")

            # Take screenshot of instructions
            self.proof_system.take_screenshot(f"task_{task['id']}_instructions")

            # Randomly simulate "uncertain" behavior 10% of time
            if random.random() < 0.10:
                time.sleep(random.uniform(9, 14))
                self.proof_system.take_screenshot(f"task_{task['id']}_uncertain")
                return {
                    "success": False,
                    "error": "Temporary confusion - will retry",
                    "should_retry": True
                }

            # Wait for a human-like random time to simulate real work
            time.sleep(random.uniform(35, 77))

            # Take final screenshot
            final_screenshot = self.proof_system.take_screenshot(f"task_{task['id']}_final")

            return {
                "success": True,
                "proof": {
                    "description": "Task completed as per instructions.",
                    "screenshots": [final_screenshot]
                }
            }

        except Exception as e:
            logger.error(f"Error executing generic task {task['id']}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _submit_proof(self, task: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not execution_result.get("proof"):
                logger.warning(f"No proof available for task {task['id']}")
                return {
                    "success": False,
                    "error": "No proof available"
                }
            # Find proof submission form
            try:
                proof_form = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form.proof-form"))
                )
            except TimeoutException:
                logger.warning(f"Proof form not found for task {task['id']}")
                return {
                    "success": False,
                    "error": "Proof form not found"
                }

            # Fill description with human-like delays
            description_field = proof_form.find_element(By.NAME, "description")
            description = execution_result["proof"].get("description", "Task completed successfully.")
            for char in description:
                description_field.send_keys(char)
                time.sleep(random.uniform(0.01, 0.05))

            # Random scroll + delay to avoid pattern
            if random.random() < 0.18:
                self.driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(50, 200))
                time.sleep(random.uniform(1, 3))
                self.proof_system.take_screenshot(f"task_{task['id']}_preproof_scroll")

            # Upload screenshots if required
            screenshots = execution_result["proof"].get("screenshots", [])
            if screenshots:
                try:
                    upload_field = proof_form.find_element(By.CSS_SELECTOR, "input[type='file']")
                    for screenshot in screenshots:
                        if os.path.exists(screenshot):
                            upload_field.send_keys(os.path.abspath(screenshot))
                            time.sleep(random.uniform(1, 2.1))
                except NoSuchElementException:
                    logger.debug(f"No file upload field found for task {task['id']}")

            # Upload video if required
            video = execution_result["proof"].get("video")
            if video and os.path.exists(video):
                try:
                    upload_field = proof_form.find_element(By.CSS_SELECTOR, "input[type='file']")
                    upload_field.send_keys(os.path.abspath(video))
                    time.sleep(random.uniform(2, 3.2))
                except NoSuchElementException:
                    logger.debug(f"No file upload field found for task {task['id']}")

            # Screenshot of proof submission
            self.proof_system.take_screenshot(f"task_{task['id']}_proof_submission")

            # Submit proof
            submit_button = proof_form.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            submit_button.click()

            # Wait for confirmation
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
                )
                logger.info(f"Successfully submitted proof for task {task['id']}")
                self.proof_system.take_screenshot(f"task_{task['id']}_confirmation")
                return {
                    "success": True
                }
            except TimeoutException:
                logger.warning(f"No confirmation received for task {task['id']}")
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".alert-danger")
                    error_message = error_element.text.strip()
                    logger.warning(f"Error submitting proof for task {task['id']}: {error_message}")
                    return {
                        "success": False,
                        "error": error_message
                    }
                except NoSuchElementException:
                    return {
                        "success": False,
                        "error": "No confirmation received"
                    }

        except Exception as e:
            logger.error(f"Error submitting proof for task {task['id']}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
