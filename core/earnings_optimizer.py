#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Earnings Optimizer Module
------------------------
Optimizes task selection based on reward, estimated time, and success rate.
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EarningsOptimizer:
    """Optimizes task selection for maximum earnings."""
    
    def __init__(self, blacklist_file: str = "freelancerfly_bot/config/blacklist.json",
                 min_reward: float = 0.10, max_failures: int = 3):
        """
        Initialize earnings optimizer.
        
        Args:
            blacklist_file: Path to blacklist file
            min_reward: Minimum reward to consider a task
            max_failures: Maximum number of failures before blacklisting a task
        """
        self.blacklist_file = blacklist_file
        self.min_reward = min_reward
        self.max_failures = max_failures
        
        # Load blacklist
        self.blacklist = self._load_blacklist()
        
        # Task statistics
        self.task_stats = {}
        
        # Estimated time per category (in seconds)
        self.estimated_times = {
            "youtube": 180,  # 3 minutes
            "telegram": 60,  # 1 minute
            "signup": 300,   # 5 minutes
            "search": 120,   # 2 minutes
            "visit": 90,     # 1.5 minutes
            "unknown": 240   # 4 minutes
        }
    
    def _load_blacklist(self) -> Dict[str, Dict[str, Any]]:
        """
        Load blacklist from file.
        
        Returns:
            Dict[str, Dict[str, Any]]: Blacklisted tasks
        """
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r') as f:
                    blacklist = json.load(f)
                logger.debug(f"Loaded blacklist from {self.blacklist_file}")
                return blacklist
            else:
                # Create empty blacklist
                os.makedirs(os.path.dirname(self.blacklist_file), exist_ok=True)
                with open(self.blacklist_file, 'w') as f:
                    json.dump({}, f)
                logger.info(f"Created empty blacklist at {self.blacklist_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading blacklist: {str(e)}")
            return {}
    
    def _save_blacklist(self):
        """Save blacklist to file."""
        try:
            os.makedirs(os.path.dirname(self.blacklist_file), exist_ok=True)
            with open(self.blacklist_file, 'w') as f:
                json.dump(self.blacklist, f, indent=2)
            logger.debug(f"Saved blacklist to {self.blacklist_file}")
        except Exception as e:
            logger.error(f"Error saving blacklist: {str(e)}")
    
    def is_blacklisted(self, task_id: str) -> bool:
        """
        Check if a task is blacklisted.
        
        Args:
            task_id: Task ID
        
        Returns:
            bool: True if task is blacklisted, False otherwise
        """
        return task_id in self.blacklist
    
    def blacklist_task(self, task_id: str, reason: str = ""):
        """
        Blacklist a task.
        
        Args:
            task_id: Task ID
            reason: Reason for blacklisting
        """
        self.blacklist[task_id] = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }
        logger.info(f"Blacklisted task {task_id}: {reason}")
        self._save_blacklist()
    
    def record_success(self, task: Dict[str, Any]):
        """
        Record a successful task completion.
        
        Args:
            task: Task information
        """
        task_id = task["id"]
        
        if task_id not in self.task_stats:
            self.task_stats[task_id] = {
                "successes": 0,
                "failures": 0,
                "total_time": 0,
                "total_reward": 0,
                "last_success": None,
                "last_failure": None
            }
        
        # Update statistics
        self.task_stats[task_id]["successes"] += 1
        self.task_stats[task_id]["total_reward"] += task["reward"]
        self.task_stats[task_id]["last_success"] = datetime.now().isoformat()
        
        # Estimate time based on category
        category = task.get("category", "unknown")
        estimated_time = self.estimated_times.get(category, 240)
        self.task_stats[task_id]["total_time"] += estimated_time
        
        logger.debug(f"Recorded success for task {task_id}")
    
    def record_failure(self, task: Dict[str, Any], error: str = ""):
        """
        Record a task failure.
        
        Args:
            task: Task information
            error: Error message
        """
        task_id = task["id"]
        
        if task_id not in self.task_stats:
            self.task_stats[task_id] = {
                "successes": 0,
                "failures": 0,
                "total_time": 0,
                "total_reward": 0,
                "last_success": None,
                "last_failure": None
            }
        
        # Update statistics
        self.task_stats[task_id]["failures"] += 1
        self.task_stats[task_id]["last_failure"] = datetime.now().isoformat()
        
        # Estimate time based on category
        category = task.get("category", "unknown")
        estimated_time = self.estimated_times.get(category, 240)
        self.task_stats[task_id]["total_time"] += estimated_time
        
        logger.debug(f"Recorded failure for task {task_id}")
        
        # Check if task should be blacklisted
        if self.task_stats[task_id]["failures"] >= self.max_failures:
            self.blacklist_task(task_id, f"Failed {self.max_failures} times. Last error: {error}")
    
    def calculate_task_value(self, task: Dict[str, Any]) -> float:
        """
        Calculate the value of a task based on reward, estimated time, and success rate.
        
        Args:
            task: Task information
        
        Returns:
            float: Task value (reward per minute * success rate)
        """
        task_id = task["id"]
        reward = task["reward"]
        category = task.get("category", "unknown")
        
        # Get estimated time based on category
        estimated_time = self.estimated_times.get(category, 240)
        
        # Calculate success rate
        if task_id in self.task_stats:
            stats = self.task_stats[task_id]
            total_attempts = stats["successes"] + stats["failures"]
            if total_attempts > 0:
                success_rate = stats["successes"] / total_attempts
            else:
                success_rate = 0.5  # Default 50% success rate for new tasks
        else:
            success_rate = 0.5  # Default 50% success rate for new tasks
        
        # Calculate reward per minute
        reward_per_minute = (reward / (estimated_time / 60))
        
        # Calculate task value
        task_value = reward_per_minute * success_rate
        
        return task_value
    
    def optimize_tasks(self, classified_tasks: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Optimize tasks for maximum earnings.
        
        Args:
            classified_tasks: Tasks grouped by category
        
        Returns:
            List[Dict[str, Any]]: Optimized list of tasks
        """
        # Flatten tasks
        all_tasks = []
        for category, tasks in classified_tasks.items():
            all_tasks.extend(tasks)
        
        # Filter out blacklisted tasks and tasks with low reward
        filtered_tasks = []
        for task in all_tasks:
            task_id = task["id"]
            reward = task["reward"]
            
            if self.is_blacklisted(task_id):
                logger.debug(f"Skipping blacklisted task {task_id}")
                continue
            
            if reward < self.min_reward:
                logger.debug(f"Skipping low-reward task {task_id} (${reward:.2f} < ${self.min_reward:.2f})")
                continue
            
            filtered_tasks.append(task)
        
        # Calculate task values
        for task in filtered_tasks:
            task["value"] = self.calculate_task_value(task)
        
        # Sort tasks by value (descending)
        optimized_tasks = sorted(filtered_tasks, key=lambda t: t["value"], reverse=True)
        
        # Log optimization results
        if optimized_tasks:
            top_task = optimized_tasks[0]
            logger.info(f"Top task: {top_task['title']} (${top_task['reward']:.2f}, value: {top_task['value']:.4f})")
        
        logger.info(f"Optimized {len(optimized_tasks)} tasks for maximum earnings")
        
        return optimized_tasks
    
    def update_estimated_time(self, category: str, time_seconds: int):
        """
        Update estimated time for a category.
        
        Args:
            category: Task category
            time_seconds: Estimated time in seconds
        """
        if category in self.estimated_times:
            # Use exponential moving average to update estimated time
            alpha = 0.2  # Weight for new observation
            old_estimate = self.estimated_times[category]
            new_estimate = (alpha * time_seconds) + ((1 - alpha) * old_estimate)
            self.estimated_times[category] = new_estimate
            
            logger.debug(f"Updated estimated time for {category}: {old_estimate:.1f}s -> {new_estimate:.1f}s")
    
    def get_earnings_report(self) -> Dict[str, Any]:
        """
        Get earnings report.
        
        Returns:
            Dict[str, Any]: Earnings report
        """
        total_earnings = 0
        total_time = 0
        total_tasks = 0
        
        for task_id, stats in self.task_stats.items():
            total_earnings += stats["total_reward"]
            total_time += stats["total_time"]
            total_tasks += stats["successes"]
        
        # Calculate earnings per hour
        if total_time > 0:
            earnings_per_hour = (total_earnings / (total_time / 3600))
        else:
            earnings_per_hour = 0
        
        report = {
            "total_earnings": total_earnings,
            "total_time_seconds": total_time,
            "total_tasks_completed": total_tasks,
            "earnings_per_hour": earnings_per_hour,
            "blacklisted_tasks": len(self.blacklist)
        }
        
        return report