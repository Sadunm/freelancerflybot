#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import threading
import time
import logging
from datetime import datetime

# ---- Always add current dir to sys.path for safe import ----
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.account_manager import AccountManager, Account
from utils.config_loader import load_config

# --------- Logging Setup (File only, no console print) ---------
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    filename=os.path.join(log_dir, f"session_{session_id}.log"),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def account_worker(account: Account, config: dict):
    try:
        driver = account.login()
        while True:
            # Example (Change type as you test different executors)
            task = {
                "id": f"demo_{account.completed_tasks+1}",
                "type": "youtube",  # try: "youtube", "visit", "search", etc.
                "description": "Watch and like: https://www.youtube.com/watch?v=7IlHqMMTyHQ"
            }
            result = account.execute_task(task)
            # Delay between tasks
            time.sleep(config.get('timing', {}).get('task_delay', 10))
            # Optional: max_tasks per account
            if account.max_tasks and account.completed_tasks >= account.max_tasks:
                break
    except Exception as e:
        logger.error(f"[{account.email}] worker crashed: {e}")
    finally:
        account.logout()

def main():
    # -------- Config Load --------
    config = load_config('config/config.json')
    accounts_cfg = load_config('config/accounts.json')
    proxies_cfg = load_config('config/proxies.json')

    # -------- Account Selection --------
    selected_accounts = accounts_cfg[:3]  # First 3 only (edit if needed)
    if len(selected_accounts) < 1:
        logger.error("At least 1 account required in accounts.json.")
        return

    # -------- Account Manager Init --------
    account_manager = AccountManager(
        accounts=selected_accounts,
        proxies=proxies_cfg,
        headless=True,
        session_id=session_id
    )

    # -------- Start Parallel Threads --------
    threads = []
    for acc in account_manager.accounts:
        t = threading.Thread(target=account_worker, args=(acc, config), daemon=True)
        threads.append(t)
        t.start()

    # -------- Keep Alive Main Thread --------
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        for acc in account_manager.accounts:
            acc.logout()
        logger.info("All accounts stopped.")

if __name__ == "__main__":
    main()
