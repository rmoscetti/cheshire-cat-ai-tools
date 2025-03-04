# Use the official cheshire cat image
FROM ghcr.io/cheshire-cat-ai/core:latest

# Install packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY install_pip_editable_deps.sh .
# need to install at runtime as they are not available at build time
CMD bash install_pip_editable_deps.sh && python3 -m cat.main 