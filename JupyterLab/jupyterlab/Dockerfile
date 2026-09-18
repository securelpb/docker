# ----------------------------------------------------
# MODERN PYTORCH & GENERATIVE AI ENVIRONMENT
# Base: NVIDIA CUDA + CUDNN Development Image for Ubuntu 24.04
# ----------------------------------------------------
FROM nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04

ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. System Packages
# Note: Kept build-essential and cmake just in case future python packages need basic C-compilation
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

# 3. User Setup
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER

# Fix permissions on the .cache folder created by BuildKit/Root
# Ensure the directory exists, then fix any root permissions left by BuildKit
RUN mkdir -p /home/$NB_USER/.cache && \
    chown -R $NB_USER:$NB_USER /home/$NB_USER/.cache

# 4. Switch to User and set up environment
USER $NB_USER
ENV PATH="/home/$NB_USER/.local/bin:${PATH}"
ENV PYTHONPATH="/home/$NB_USER/work/jupyterlab/securesmith:${PYTHONPATH}"
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Needed for GTX 1080
ENV PIP_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cu121"

# 2. Create a permanent constraint file to lock the PyTorch ecosystem for GTX 1080
ENV PIP_CONSTRAINT="/home/$NB_USER/.pip_constraints.txt"
RUN echo "torch<2.6" > /home/$NB_USER/.pip_constraints.txt && \
    echo "torchvision<0.22" >> /home/$NB_USER/.pip_constraints.txt && \
    echo "torchaudio<2.6" >> /home/$NB_USER/.pip_constraints.txt

# 5. User SSH Setupß
RUN mkdir -p /home/$NB_USER/.ssh && \
    chmod 700 /home/$NB_USER/.ssh

COPY --chown=$NB_USER:$NB_GID ssh_keys/authorized_keys /home/$NB_USER/.ssh/authorized_keys
RUN chmod 600 /home/$NB_USER/.ssh/authorized_keys

# ==========================================
# PACKAGE INSTALLATION
# ==========================================

# ==========================================
# UPGRADE PIP
# ==========================================
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,uid=1000,gid=1000 \
    pip install --upgrade pip setuptools wheel

# LAYER 1: The "Heavy" PyTorch Foundation
# We isolate this so Docker caches the massive 3GB download permanently.
# Pinned to 2.6 for GTX 1080
RUN python3 -m pip install --no-cache-dir \
    "torch" \
    "torchvision" \
    "torchaudio"

# LAYER 1.5: Supplementary PyTorch Tools
# Installed from standard PyPI
RUN python3 -m pip install --no-cache-dir \
    "accelerate" \
    "torchao>=0.17.0"

# LAYER 2: The "Agile" Data Science & Tools Layer
# All other tools are combined into one command so pip's dependency resolver
# can map out the perfect version tree without conflicts.
RUN python3 -m pip install --no-cache-dir \
    # --- Key Libraries ---
    diffusers \
    xformers \
    transformers \
    opencv-contrib-python-headless \
    Pillow \
    "bitsandbytes>0.43" \
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
    lightgbm \
    catboost \
    optuna \
    # --- Visualization ---
    matplotlib \
    plotly \
    seaborn \
    shap \
    wordcloud \
    # --- Generative AI ---
    huggingface_hub \
    datasets \
    # --- Jupyter & IDE ---
    jupyterlab \
    ipykernel \
    ipywidgets \
    jupyterlab_code_formatter \
    jupyterlab_execute_time \
    lckr_jupyterlab_variableinspector \
    jupyterlab-git \
    jupytext \
    notebook \
    # --- Utilities & Other --- \
    tensorboard \
    beautifulsoup4 \
    Faker \
    featuretools \
    Flask \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    google-genai \
    langchain \
    langchain-community \
    langchain-chroma \
    chromadb \
    openai \
    libarchive-c \
    mediapy \
    moviepy \
    nltk \
    openpyxl \
    pydub \
    black \
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