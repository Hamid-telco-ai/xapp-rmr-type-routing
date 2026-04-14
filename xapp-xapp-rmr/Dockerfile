FROM python:3.11-bullseye

ARG RMR_VER=4.9.0

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/libexec

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    curl \
    gnupg \
    libssl-dev \
    build-essential \
    gcc \
    libc6 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -nv -O /tmp/rmr_${RMR_VER}_amd64.deb \
      https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/rmr_${RMR_VER}_amd64.deb/download.deb \
    && wget -nv -O /tmp/rmr-dev_${RMR_VER}_amd64.deb \
      https://packagecloud.io/o-ran-sc/release/packages/debian/stretch/rmr-dev_${RMR_VER}_amd64.deb/download.deb \
    && dpkg -i /tmp/rmr_${RMR_VER}_amd64.deb /tmp/rmr-dev_${RMR_VER}_amd64.deb \
    && rm -f /tmp/rmr_${RMR_VER}_amd64.deb /tmp/rmr-dev_${RMR_VER}_amd64.deb \
    && ldconfig \
    && ls -l /usr/local/lib/librmr_si.so*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/

ENV RMR_SEED_RT=/app/routes.rtg
ENV RMR_RTG_SVC=-1
ENV RMR_PORT=4560
ENV PING_MTYPE=10000
ENV PONG_MTYPE=10001
ENV RMR_VLEVEL=3

CMD ["python", "/app/hello.py"]