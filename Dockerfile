# https://github.com/atlassian/docker-chromium-xvfb/blob/master/images/base/xvfb-chromium
FROM debian:stable
ENV DEBIAN_FRONTEND=noninteractive
ARG VNC_PASSWORD="password"

RUN \
  apt update \
  && apt install -y \
    awesome \
    chromium \
    chromium-driver \
    curl \
    htop \
    iproute2 \
    nano \
    procps \
    python3 \
    python3-pip \
    wget \
    x11vnc \
    xvfb \
  && mkdir -p /root/.vnc \
  && x11vnc -storepasswd $VNC_PASSWORD /root/.vnc/passwd

WORKDIR /opt/src
COPY . /opt/src/

# Allow pip to install packages in Python 3.12+ externally-managed environment
ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN python3 -m pip install --upgrade pip \
  && python3 -m pip install --no-cache-dir -r requirements.txt

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV CHROME_BINARY=/usr/bin/chromium
ENV HEADLESS=true

COPY docker-entrypoint /usr/bin/docker-entrypoint
RUN chmod +x /usr/bin/docker-entrypoint

ENTRYPOINT ["/usr/bin/docker-entrypoint"]
CMD ["python3", "run_staged_multi_loop_wh.py"]
