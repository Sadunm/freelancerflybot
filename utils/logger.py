#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Logger Module
----------
Sets up logging for the bot.
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional

def setup_logger(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logger.
    
    Args:
        log_file: Path to log file
        level: Logging level
    
    Returns:
        logging.Logger: Logger instance
    """
    # Create logger
    logger = logging.getLogger("freelancerfly_bot")
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Create error log file
    if log_file:
        error_log_file = log_file.replace(".log", "_error.log")
        
        # Create error file handler
        error_file_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)
    
    # Log setup
    logger.info(f"Logger initialized (level: {logging.getLevelName(level)})")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    
    return logger

def get_logger() -> logging.Logger:
    """
    Get logger instance.
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger("freelancerfly_bot")

class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for adding context to log messages."""
    
    def __init__(self, logger, extra=None):
        """
        Initialize logger adapter.
        
        Args:
            logger: Logger instance
            extra: Extra context
        """
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        """
        Process log message.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
        
        Returns:
            tuple: Processed message and keyword arguments
        """
        # Add context to message
        context_str = " ".join(f"[{k}={v}]" for k, v in self.extra.items())
        if context_str:
            msg = f"{context_str} {msg}"
        
        return msg, kwargs

def get_account_logger(account_email: str) -> logging.LoggerAdapter:
    """
    Get logger adapter for an account.
    
    Args:
        account_email: Account email
    
    Returns:
        logging.LoggerAdapter: Logger adapter
    """
    logger = get_logger()
    return LoggerAdapter(logger, {"account": account_email})

def get_task_logger(task_id: str, account_email: Optional[str] = None) -> logging.LoggerAdapter:
    """
    Get logger adapter for a task.
    
    Args:
        task_id: Task ID
        account_email: Account email
    
    Returns:
        logging.LoggerAdapter: Logger adapter
    """
    logger = get_logger()
    extra = {"task": task_id}
    if account_email:
        extra["account"] = account_email
    return LoggerAdapter(logger, extra)