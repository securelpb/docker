# ----------------------------------------------------
# UNIFIED ML ENVIRONMENT (RTX 3090 / Compute 8.6)
# PyTorch + TensorFlow + DGL + JupyterLab + SSH
# ----------------------------------------------------
# Base Image: Ubuntu 24.04 + CUDA 12.6.2 + cuDNN
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04

# NVIDIA & TensorFlow Environment Variables (Mimicking NGC Optimizations)
ENV DEBIAN_FRONTEND=noninteractive
ENV TF_CUDA_COMPUTE_CAPABILITIES="8.6"
ENV NVIDIA_VISIBLE_DEVICES="all"
ENV NVIDIA_DRIVER_CAPABILITIES="compute,utility"
ENV TF_FORCE_GPU_ALLOW_GROWTH="true"
ENV TF_CUDNN_USE_AUTOTUNE="1"
ENV TF_XLA_FLAGS="--tf_xla_auto_jit=2"
ENV DGLBACKEND=pytorch

ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# System Packages & Root-level setup
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    tini \
    openssh-server \
    libarchive-dev \
    python3.12 \
    python3.12-dev \
    python3-pip \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# SSH Configuration
# -----------------
# Create a directory for the SSH daemon
RUN mkdir -p /var/run/sshd

# Copy pre-generated host keys from the build context.
COPY jupyterlab/ssh_keys/ssh_host_*_key /etc/ssh/
COPY jupyterlab/ssh_keys/ssh_host_*_key.pub /etc/ssh/

# Set strict permissions for the host keys and verify them.
# sshd will refuse to start if private keys are group/world-readable.
RUN echo "---- Verifying SSH key permissions ----" && \
    ls -l /etc/ssh/ && \
    chmod 600 /etc/ssh/ssh_host_rsa_key /etc/ssh/ssh_host_ecdsa_key /etc/ssh/ssh_host_ed25519_key && \
    chmod 644 /etc/ssh/ssh_host_rsa_key.pub /etc/ssh/ssh_host_ecdsa_key.pub /etc/ssh/ssh_host_ed25519_key.pub && \
    echo "---- Permissions after chmod ----" && \
    ls -l /etc/ssh/

# Configure sshd to use public key authentication and disable passwords
RUN echo "Port 22" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "AuthorizedKeysFile .ssh/authorized_keys" >> /etc/ssh/sshd_config

# Copy and set permissions for the entrypoint script while still root
COPY jupyterlab/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Alias python3 to python explicitly
RUN ln -sf /usr/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.12 /usr/bin/python

# Create a symlink for the CUDA stub library
RUN mkdir -p /usr/local/cuda/lib64/stubs && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 || true

# User Setup [cite: 4, 15]
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER && \
    git config --system credential.helper 'cache --timeout=34560000'

# Fix permissions on the .cache folder created by BuildKit/Root
# Ensure the directory exists, then fix any root permissions left by BuildKit
RUN mkdir -p /home/$NB_USER/.cache && \
    chown -R $NB_USER:$NB_USER /home/$NB_USER/.cache

# Switch to user & Bypass PEP 668 for system/user pip installs
USER $NB_USER
ENV PATH="/home/$NB_USER/.local/bin:${PATH}"
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# SSH setup for the user
# ----------------------
# Create .ssh directory and copy the authorized_keys file
RUN mkdir -p /home/$NB_USER/.ssh
COPY --chown=$NB_USER:$NB_GID jupyterlab/ssh_keys/authorized_keys /home/$NB_USER/.ssh/authorized_keys

# Set correct, strict permissions for the user's SSH files
RUN chmod 700 /home/$NB_USER/.ssh && \
    chmod 600 /home/$NB_USER/.ssh/authorized_keys

# ==========================================
# 1. UPGRADE PIP (Rarely changes)
# ==========================================
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install --upgrade pip setuptools wheel

# ==========================================
# 2. THE HEAVYWEIGHTS (Rarely changes, huge downloads)
# ==========================================
# A. PyTorch Ecosystem (Locked to 2.4.0)
# Note: Base image is CUDA 12.6, but PyTorch is for CUDA 12.4.
# This should be fine due to CUDA's backward compatibility.
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install "torch==2.4.0" "torchvision==0.19.0" "torchaudio==2.4.0" \
    --index-url https://download.pytorch.org/whl/cu124

# B. DGL
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install dgl -f https://data.dgl.ai/wheels/torch-2.4/cu124/repo.html

# C. Naked TensorFlow
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install "tensorflow>=2.17.0" "tensorboard"

# ==========================================
# 3. LLAMA-CPP COMPILATION (Rarely changes, slow C++ build)
# ==========================================
# Notice: Removed --no-cache-dir so the cache mount actually works!
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH \
    CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=86" \
    pip install "llama-cpp-python < 1"

# ==========================================
# 4. STANDARD PACKAGES (Changes frequently)
# ==========================================
# If you add a package here tomorrow, Docker instantly uses the cached
# layers for Steps 1, 2, and 3. It will only rebuild from this step down!
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000  \
    pip install \
    "beautifulsoup4 < 5" \
    "cupy" \
    dask-ml \
    "datasets < 5" \
    "decorator < 6" \
    Faker \
    "Flask < 4" \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    "huggingface_hub[cli] < 2" \
    imblearn \
    ipykernel \
    ipywidgets \
    jupyterlab \
    jupyterlab_code_formatter \
    jupyterlab_execute_time \
    jupyterlab-git \
    jupytext \
    keras-tuner \
    "kmedoids < 1" \
    "kneed < 1" \
    "libarchive-c" \
    "matplotlib < 4" \
    git+https://github.com/AbdullahO/mSSA.git@a7b25f5 \
    "nbformat < 6" \
    "networkx < 4" \
    nltk \
    notebook \
    "numpy < 2" \
    "opencv-contrib-python-headless < 5" \
    "openpyxl < 4" \
    "pandas < 4" \
    pandas-stubs \
    "pydevd-pycharm~=253.31033.139" \
    "plotly < 7" \
    "pmdarima >= 2.1.0" \
    "pytest < 10" \
    "scikeras>=0.13.0" \
    "scikit-image < 1" \
    "scikit-learn" \
    scikit-learn-extra \
    "scipy < 2" \
    scipy-stubs \
    "seaborn < 1" \
    "shap < 1" \
    "sklearn-compat < 1" \
    "sklearn-pandas < 3" \
    "statsmodels < 1" \
    surprise \
    "xgboost < 4" \
    "ydata-profiling < 5"

# ==========================================
# 5. THE SLEDGEHAMMER (Dead last to hide it from pip's dependency checker)
# ==========================================
# Force-upgrade the shadow CuDNN library to satisfy TensorFlow.
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install --no-deps "nvidia-cudnn-cu12>=9.3.0.75"

# Jupyter specific configurations
RUN jupyter labextension enable jupyterlab-execute-time

# Register Kernel
RUN python3 -m ipykernel install --user --name=python3 --display-name="Python 3 (TF + PyTorch)"

# Jupyter Configuration JSON
RUN mkdir -p /home/$NB_USER/.jupyter/lab/settings && \
    echo '{\n\
  "@jupyterlab/notebook-extension:tracker": {\n\
    "recordTiming": true\n\
  }\n\
}' > /home/$NB_USER/.jupyter/lab/settings/overrides.json

WORKDIR /home/$NB_USER
EXPOSE 8888 6006 22

# Use tini to manage the entrypoint script, which in turn starts sshd and Jupyter
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]
