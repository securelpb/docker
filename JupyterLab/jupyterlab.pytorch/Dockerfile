# ----------------------------------------------------
# MODERN PYTORCH & GENERATIVE AI ENVIRONMENT
# Base: NVIDIA CUDA + CUDNN Development Image for Ubuntu 24.04
# Strategy: Mirror the stable 'jupyterlab' service foundation, but with a modern package set.
# ----------------------------------------------------
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04

ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. System Packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    tini \
    wget \
    openssh-server \
    libarchive-dev \
    python3.12 \
    python3.12-dev \
    python3-pip \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. SSH Configuration
RUN mkdir -p /var/run/sshd
COPY ssh_keys/ssh_host_*_key /etc/ssh/
COPY ssh_keys/ssh_host_*_key.pub /etc/ssh/
RUN chmod 600 /etc/ssh/ssh_host_*_key && \
    echo "Port 22" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication no" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "AuthorizedKeysFile .ssh/authorized_keys" >> /etc/ssh/sshd_config
COPY jupyterlab/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create a symlink for the CUDA stub library, which is needed by some build processes.
RUN mkdir -p /usr/local/cuda/lib64/stubs && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 || true

# 3. User Setup
# Evict any existing user/group on UID/GID 1000, then create our user.
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER

# 4. Switch to User and set up environment
USER $NB_USER
ENV PATH="/home/$NB_USER/.local/bin:${PATH}"
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# 5. User SSH Setup
RUN mkdir -p /home/$NB_USER/.ssh && \
    chmod 700 /home/$NB_USER/.ssh
COPY --chown=$NB_USER:$NB_GID ssh_keys/authorized_keys /home/$NB_USER/.ssh/authorized_keys
RUN chmod 600 /home/$NB_USER/.ssh/authorized_keys

# ==========================================
# PACKAGE INSTALLATION
# ==========================================

# A. Install the Holy Trinity first, using the default PyPI index.
RUN python3 -m pip install \
    "torch" \
    "torchvision" \
    "torchaudio" \
    "accelerate" \
    "torchao>=0.17.0"

# ==========================================
# 3. LLAMA-CPP COMPILATION (Rarely changes, slow C++ build)
# ==========================================
# Notice: Removed --no-cache-dir so the cache mount actually works!
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH \
    CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=86" \
    pip install "llama-cpp-python[server]"


# B. Install the build system tools in their own layer.
RUN python3 -m pip install --no-build-isolation \
    scikit-build-core

# C. Install the rest of the packages.
# CMAKE_ARGS are needed for llama-cpp-python compilation.
RUN CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=86" \
    python3 -m pip install --no-build-isolation \
    # --- Key Libraries ---
    diffusers \
    transformers \
    opencv-contrib-python-headless \
    # --- The New Hotness ---
    suno-bark \
    # --- Core Data Science & ML ---
    numpy \
    pandas \
    pandas-stubs \
    scipy \
    scipy-stubs \
    scikit-image \
    scikit-learn \
    statsmodels \
    xgboost \
    # --- Visualization ---
    matplotlib \
    plotly \
    seaborn \
    shap \
    # --- Generative AI ---
    huggingface_hub \
    datasets \
    # --- Jupyter & IDE ---
    jupyterlab \
    ipykernel \
    ipywidgets \
    jupyterlab_code_formatter \
    jupyterlab_execute_time \
    jupyterlab-git \
    jupytext \
    notebook \
    "pydevd-pycharm~=253.31033.139" \
    # --- Utilities & Other ---
    beautifulsoup4 \
    Faker \
    Flask \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    google-genai \
    libarchive-c \
    mediapy \
    moviepy \
    nltk \
    openpyxl \
    pydub \
    pytest \
    ydata-profiling \
    git+https://github.com/AbdullahO/mSSA.git@a7b25f5

# ==========================================
# JUPYTER CONFIGURATION
# ==========================================
RUN jupyter labextension enable jupyterlab-execute_time
RUN python3 -m ipykernel install --user --name=pytorch_modern --display-name="Python (Modern PyTorch)"
RUN mkdir -p /home/$NB_USER/.jupyter/lab/settings && \
    echo '{\n\
  "@jupyterlab/notebook-extension:tracker": {\n\
    "recordTiming": true\n\
  }\n\
}' > /home/$NB_USER/.jupyter/lab/settings/overrides.json

WORKDIR /home/jovyan
EXPOSE 8888 22

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]
