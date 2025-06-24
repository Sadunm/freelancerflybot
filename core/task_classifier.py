#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Task Classifier Module
---------------------
Classifies tasks into different categories based on their title and description.
"""

import re
import logging
from typing import Dict, Any, List
import json
import os

logger = logging.getLogger(__name__)

class TaskClassifier:
    """Classifies tasks into different categories."""

    CATEGORY_YOUTUBE = "youtube"
    CATEGORY_TELEGRAM = "telegram"
    CATEGORY_SIGNUP = "signup"
    CATEGORY_SEARCH = "search"
    CATEGORY_VISIT = "visit"
    CATEGORY_UNKNOWN = "unknown"

    def __init__(self, keywords_file: str = "freelancerfly_bot/config/keywords.json"):
        self.keywords_file = keywords_file
        self.keywords = self._load_keywords()

    def _load_keywords(self) -> Dict[str, List[str]]:
        default_keywords = {
            self.CATEGORY_YOUTUBE: ["youtube", "watch", "video", "subscribe", "channel", "like", "comment"],
            self.CATEGORY_TELEGRAM: ["telegram", "join", "group", "t.me", "chat"],
            self.CATEGORY_SIGNUP: ["signup", "sign up", "register", "create account", "join", "registration"],
            self.CATEGORY_SEARCH: ["search", "google", "bing", "find", "query", "look up"],
            self.CATEGORY_VISIT: ["visit", "website", "page", "browse", "click", "link"]
        }
        try:
            if os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                os.makedirs(os.path.dirname(self.keywords_file), exist_ok=True)
                with open(self.keywords_file, 'w', encoding='utf-8') as f:
                    json.dump(default_keywords, f, indent=2)
                return default_keywords
        except Exception as e:
            logger.error(f"Error loading keywords: {str(e)}")
            return default_keywords

    def classify_task(self, task: Dict[str, Any]) -> str:
        title = task.get("title", "").lower()
        description = task.get("description", "").lower()
        text = f"{title} {description}"

        for category, keywords in self.keywords.items():
            if any(keyword in text for keyword in keywords):
                return category

        if re.search(r'youtube\.com|youtu\.be', text):
            return self.CATEGORY_YOUTUBE
        if re.search(r't\.me|telegram\.org', text):
            return self.CATEGORY_TELEGRAM

        return self.CATEGORY_UNKNOWN

    def classify_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        classified = {
            self.CATEGORY_YOUTUBE: [],
            self.CATEGORY_TELEGRAM: [],
            self.CATEGORY_SIGNUP: [],
            self.CATEGORY_SEARCH: [],
            self.CATEGORY_VISIT: [],
            self.CATEGORY_UNKNOWN: []
        }
        for task in tasks:
            if "description" not in task and "task_fetcher" in task:
                fetcher = task["task_fetcher"]
                task_details = fetcher.get_task_details(task["id"])
                if task_details:
                    task.update(task_details)

            category = self.classify_task(task)
            task["category"] = category
            classified[category].append(task)

        return classified

    def update_keywords(self, category: str, keywords: List[str]):
        if category not in self.keywords:
            logger.error(f"Invalid category: {category}")
            return
        self.keywords[category] = keywords
        try:
            os.makedirs(os.path.dirname(self.keywords_file), exist_ok=True)
            with open(self.keywords_file, 'w', encoding='utf-8') as f:
                json.dump(self.keywords, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving keywords: {str(e)}")
