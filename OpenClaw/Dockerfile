FROM ghcr.io/openclaw/openclaw:latest

# Switch to root to perform system installations
USER root

# Clean out any old Go installations if present
RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
    curl \
    net-tools \
    ca-certificates \
    vim \
    openssh-client \
    sudo \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Grant sudo access to the 'node' user
RUN usermod -aG sudo node && echo "node ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/node

# Install the stable Go compiler (Go 1.24.0) directly from the source binaries
RUN curl -L https://golang.org/dl/go1.24.0.linux-amd64.tar.gz | tar -C /usr/local -xzf -

# Install the Go compiler and uv globally to /usr/local/bin
# We use UV_UNMANAGED_INSTALL to block it from trying to edit shell profiles
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/usr/local/bin" sh

# Add the new Go binary folder permanently to the container system PATH
ENV PATH="/usr/local/go/bin:${PATH}"

# Drop safely back down to the restricted user
USER node
