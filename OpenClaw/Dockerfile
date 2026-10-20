FROM node:26-bookworm

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
    python3  \
    python3-pip \
    git \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# 1. Grant sudo access to the 'node' user
RUN usermod -aG sudo node && echo "node ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/node

# 2. Install the stable Go compiler (Go 1.24.0) directly from the source binaries
RUN curl -L https://golang.org/dl/go1.24.0.linux-amd64.tar.gz | tar -C /usr/local -xzf -

# 3. Install the Go compiler and uv globally to /usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/usr/local/bin" sh

# 4. Add the new Go binary folder permanently to the container system PATH
ENV PATH="/usr/local/go/bin:${PATH}"

# Global configuration for npm to allow the node user to install global tools safely
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH="/home/node/.npm-global/bin:${PATH}"

# Drop safely back down to the restricted user
USER node
WORKDIR /home/node

# Create standard directories for OpenClaw config and persistent workspace
RUN mkdir -p /home/node/.openclaw /home/node/workspace /home/node/.npm-global /home/node/

# Install OpenClaw globally into the user's localized npm global directory
RUN npm i -g openclaw

RUN npm i -g mcporter

# Create our unmasked skills directory
RUN mkdir -p /home/node/skills

# Copy your local skill into the image
COPY --chown=node:node ./skills/ /home/node/skills/

# Concatenate all requirements.txt files and install dependencies
RUN find /home/node/skills -name "requirements.txt" -exec awk 1 {} + > /home/node/skills/all_requirements.txt && \
    sudo pip3 install --no-cache-dir --break-system-packages -r /home/node/skills/all_requirements.txt



# Expose the default OpenClaw Gateway port
EXPOSE 18789

# Start the gateway service
CMD ["openclaw", "gateway"]