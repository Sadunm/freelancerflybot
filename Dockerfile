# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Firefox and dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.31.0-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.31.0-linux64.tar.gz \
    && chmod +x /usr/local/bin/geckodriver

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for logs and proofs
RUN mkdir -p logs proofs config

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Create entrypoint script
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1366x768x16 &\npython -m freelancerfly_bot.main "$@"' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["--headless", "--log-level", "INFO"]