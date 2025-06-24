# FreelancerFly Bot

A production-grade, real-time income-generating automation bot for [FreelancerFly](https://freelancerfly.com/micro-works).

## Features

### 🛡️ Anti-Detection + Stealth Framework
- Canvas fingerprint spoofing
- WebGL noise injection
- Font and AudioContext masking
- TLS fingerprint rotation
- Randomized `navigator.webdriver` override
- Dynamic user-agent + language + timezone spoofing
- Bezier-curve mouse movement + realistic scroll
- Typing simulation with typos + corrections
- Session isolation using Firefox profiles

### 🔐 Multi-Account Management
- Input: `accounts.json` (email, password, max_tasks, headless, proxy)
- Proxy rotation per account
- Auto-retry on login failure
- Session cookies saved per account

### 📊 Task Fetcher + Reward Engine
- Navigate to `/micro-works`
- Scrape all tasks via `.job-post-horizontal-title a`
- Extract title + reward from surrounding HTML
- Sort by reward / estimated time
- Auto-blacklist low-reward or failing tasks

### 🧠 Task Classifier
- Categories: `youtube`, `telegram`, `signup`, `search`, `visit`, `unknown`
- Uses keywords for classification

### 🤖 Task Execution Modules
- **YouTube**: Watch videos with human-like behavior
- **Telegram**: Join groups and interact
- **Signup**: Create accounts with fake data
- **Search**: Perform searches and browse results
- **Visit**: Browse websites with realistic behavior

### 📸 Proof System
- Screenshot before + after task
- Smart element highlighting
- Screen recording for video tasks
- OCR verification
- Timestamp watermarking
- Description auto-fill
- Submit proof via form

### 💵 Earnings Optimization Engine
- Task value calculation: (Reward / Time) * Success Rate
- Auto-blacklist after 3 failures
- Concurrent task execution
- Reward rate tracking

### 🔧 Error Handling + Resilience
- Auto-retry on task failure
- Restart browser if hung
- Comprehensive logging
- System resource monitoring
- Telegram alerts on crash

### 📈 Logging + Monitoring System
- Detailed logs for sessions, tasks, and errors
- Screenshot storage
- Resource usage monitoring

## Installation

### Prerequisites
- Python 3.10+
- Firefox ESR
- GeckoDriver

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/freelancerfly_bot.git
cd freelancerfly_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure accounts:
Edit `config/accounts.json` with your FreelancerFly account details:
```json
[
  {
    "email": "your_email@example.com",
    "password": "your_password",
    "max_tasks": 0,
    "headless": true,
    "proxy_index": 0
  }
]
```

4. Configure proxies (optional):
Edit `config/proxies.json` with your proxy details:
```json
[
  {
    "ip": "proxy_ip",
    "port": "proxy_port",
    "username": "proxy_username",
    "password": "proxy_password",
    "country": "US",
    "type": "http"
  }
]
```

5. Configure general settings:
Edit `config/config.json` to adjust bot behavior.

## Usage

Run the bot:
```bash
python -m freelancerfly_bot.main
```

### Command-line Options
- `--config`: Path to configuration file
- `--accounts`: Path to accounts file
- `--proxies`: Path to proxies file
- `--headless`: Run in headless mode
- `--max-tasks`: Maximum number of tasks to complete (0 for unlimited)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Project Structure

```
freelancerfly_bot/
├── core/                  # Core components
│   ├── account_manager.py # Account management
│   ├── browser_manager.py # Browser management with anti-detection
│   ├── task_fetcher.py    # Task fetching
│   ├── task_classifier.py # Task classification
│   └── earnings_optimizer.py # Earnings optimization
├── modules/               # Task execution modules
│   ├── task_executor.py   # Base task executor
│   ├── youtube_executor.py # YouTube task execution
│   ├── telegram_executor.py # Telegram task execution
│   ├── signup_executor.py # Signup task execution
│   ├── search_executor.py # Search task execution
│   └── visit_executor.py  # Visit task execution
├── utils/                 # Utility modules
│   ├── proof_system.py    # Proof generation
│   ├── human_behavior.py  # Human-like behavior simulation
│   ├── stealth.py         # Anti-detection measures
│   ├── fake_data.py       # Fake data generation
│   ├── temp_mail.py       # Temporary email client
│   ├── proxy_manager.py   # Proxy management
│   ├── resource_monitor.py # System resource monitoring
│   ├── notification.py    # Notification system
│   ├── logger.py          # Logging setup
│   ├── config_loader.py   # Configuration loading
│   ├── user_agents.py     # User agent management
│   └── fingerprint.py     # Browser fingerprint management
├── config/                # Configuration files
│   ├── config.json        # General configuration
│   ├── accounts.json      # Account details
│   └── proxies.json       # Proxy details
├── logs/                  # Log files
├── proofs/                # Proof screenshots and recordings
└── main.py                # Main entry point
```

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The authors are not responsible for any misuse or violations of FreelancerFly's terms of service.

## License

This project is licensed under the MIT License - see the LICENSE file for details.