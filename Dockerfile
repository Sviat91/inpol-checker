# Docker image for inpol-checker with Google Chrome (for undetected-chromedriver), Xvfb and VNC
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ARG VNC_PASSWORD="password"

# Install system dependencies (except Chrome - will install separately)
RUN apt update && apt install -y \
    wget \
    gnupg \
    fluxbox \
    x11vnc \
    xvfb \
    build-essential \
    libffi-dev \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (official, for undetected-chromedriver compatibility)
RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && apt update \
  && apt install -y /tmp/google-chrome-stable_current_amd64.deb \
  && rm /tmp/google-chrome-stable_current_amd64.deb \
  && rm -rf /var/lib/apt/lists/*

# Setup VNC password
RUN mkdir -p /root/.vnc \
  && x11vnc -storepasswd $VNC_PASSWORD /root/.vnc/passwd

# Set working directory
WORKDIR /opt/src

# Copy application files
COPY requirements.txt /opt/src/
COPY docker-entrypoint /usr/bin/docker-entrypoint
RUN chmod +x /usr/bin/docker-entrypoint

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . /opt/src/

# Set environment variables for Chrome
# Note: CHROMEDRIVER_PATH not set - undetected-chromedriver manages driver automatically
ENV CHROME_BINARY=/usr/bin/google-chrome

ENTRYPOINT ["/usr/bin/docker-entrypoint"]
CMD ["python", "run_staged_multi_loop_wh.py"]
