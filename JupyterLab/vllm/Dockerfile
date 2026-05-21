# ----------------------------------------------------
# VLLM OPENAI-COMPATIBLE API SERVER
# Base: NVIDIA CUDA + CUDNN Development Image for Ubuntu 24.04
# ----------------------------------------------------
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04

ARG NB_USER=vllm
ARG NB_UID=1001
ARG NB_GID=1001

# 1. System Packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    wget \
    python3.12 \
    python3.12-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. User Setup
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER

# 3. Switch to User and set up environment
USER $NB_USER
ENV PATH="/home/$NB_USER/.local/bin:${PATH}"
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# 4. Install vLLM
RUN python3 -m pip install vllm

WORKDIR /home/vllm
EXPOSE 8000

CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", "--model", "meta-llama/Meta-Llama-3-8B-Instruct", "--host", "0.0.0.0"]
