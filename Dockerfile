# Simplified Docker image for inpol-checker with Chromium, Xvfb and VNC
FROM debian:stable

ENV DEBIAN_FRONTEND=noninteractive
ARG VNC_PASSWORD="password"

# Install system dependencies
RUN apt update && apt install -y \
    chromium \
    chromium-driver \
    fluxbox \
    python3 \
    python3-pip \
    x11vnc \
    xvfb \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /root/.vnc \
  && x11vnc -storepasswd $VNC_PASSWORD /root/.vnc/passwd \
  && rm -f /usr/lib/python*/EXTERNALLY-MANAGED

# Set working directory
WORKDIR /opt/src

# Copy application files
COPY requirements.txt /opt/src/
COPY docker-entrypoint /usr/bin/docker-entrypoint
RUN chmod +x /usr/bin/docker-entrypoint

# Install Python dependencies (pip 25.1.1 from apt is already up to date)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . /opt/src/

# Set environment variables for Chrome and Selenium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV CHROME_BINARY=/usr/bin/chromium
ENV HEADLESS=true

ENTRYPOINT ["/usr/bin/docker-entrypoint"]
CMD ["python3", "run_staged_multi_loop_wh.py"]
