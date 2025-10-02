# Dockerfile for Cursor Background Agents
# This provides the base environment for background agents
# Version: 1.0 - Initial setup

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nodejs \
    npm \
    vim \
    nano \
    htop \
    tree \
    unzip \
    zip \
    jq \
    openssh-client \
    ca-certificates \
    gnupg \
    rsync \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN python3 -m pip install --upgrade pip

# Create user and set up home directory
RUN useradd -m -s /bin/bash ubuntu
USER ubuntu
WORKDIR /home/ubuntu

# Set up basic shell configuration
RUN echo 'export PATH=$PATH:/home/ubuntu/.local/bin' >> /home/ubuntu/.bashrc && \
    echo 'alias ll="ls -la"' >> /home/ubuntu/.bashrc && \
    echo 'alias la="ls -A"' >> /home/ubuntu/.bashrc && \
    echo 'alias l="ls -CF"' >> /home/ubuntu/.bashrc
