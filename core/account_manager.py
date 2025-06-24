# core/account_manager.py

import time

from modules.youtube_executor import YouTubeTaskExecutor
from modules.visit_executor import VisitTaskExecutor
from modules.search_executor import SearchTaskExecutor
# import আরও লাগলে এভাবেই

class Account:
    def __init__(self, info):
        self.email = info.get("email")
        self.password = info.get("password")
        self.max_tasks = info.get("max_tasks", 0)
        self.completed_tasks = 0
        self.headless = info.get("headless", True)
        self.proxy_index = info.get("proxy_index", None)
        self.driver = None

        # (এখনই ইনিশিয়ালাইজ করার দরকার নাই; login() এ কর)
        self.proof_system = None

    def login(self):
        print(f"[LOGIN] {self.email}")
        # (ডেমো: পুরা selenium driver এখানে বসবে, প্রুফ সিস্টেমও)
        from selenium import webdriver
        self.driver = webdriver.Firefox() # টেস্টে ঠিক মত proxy/headless দে
        from freelancerfly_bot.utils.proof_system import ProofSystem  # ধরে নিছি proof_system.py utility তোর কাছে আছে
        self.proof_system = ProofSystem(self.driver)
        return self.driver

    def execute_task(self, task):
        # ধর: task dict-এ "type" key আছে ("youtube", "visit", "search" etc)
        task_type = task.get("type", "")
        result = None

        if task_type == "youtube":
            yt_executor = YouTubeTaskExecutor(self.driver, self.proof_system)
            result = yt_executor.execute(task)
        elif task_type == "visit":
            visit_executor = VisitTaskExecutor(self.driver, self.proof_system)
            result = visit_executor.execute(task)
        elif task_type == "search":
            search_executor = SearchTaskExecutor(self.driver, self.proof_system)
            result = search_executor.execute(task)
        else:
            print(f"[TASK] {self.email} doing task {task['id']}")
            time.sleep(1)
            result = True

        self.completed_tasks += 1
        return result

    def logout(self):
        print(f"[LOGOUT] {self.email}")
        if self.driver:
            self.driver.quit()
            self.driver = None

class AccountManager:
    def __init__(self, accounts, proxies, headless=True, session_id=None):
        self.accounts = [Account(acc) for acc in accounts]
        self.proxies = proxies
        self.headless = headless
        self.session_id = session_id
