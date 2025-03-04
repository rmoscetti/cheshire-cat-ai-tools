# Use the official cheshire cat image
FROM ghcr.io/cheshire-cat-ai/core:latest

# Install packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*