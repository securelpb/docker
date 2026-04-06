# ----------------------------------------------------
# MODERN PYTORCH & GENERATIVE AI ENVIRONMENT
# ----------------------------------------------------
FROM nvcr.io/nvidia/pytorch:26.03-py3

ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. System Packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    libarchive-dev \
    openssh-server \
    tini \
    && rm -rf /var/lib/apt/lists/*

# 2. SSH Configuration
RUN mkdir /var/run/sshd
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
# Evict the default 'ubuntu' user if it exists on UID/GID 1000.
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER

# Restore the constraint file as root, before switching to the user.
RUN (cp /etc/pip/original_constraint.txt /etc/pip/constraint.txt || true)

# 4. Virtual Environment (with access to NVIDIA's PyTorch)
ENV VIRTUAL_ENV=/opt/jupyter_env
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV && \
    chown -R $NB_USER:$NB_GID $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
USER $NB_USER

# 5. User SSH Setup
RUN mkdir -p /home/$NB_USER/.ssh && \
    chmod 700 /home/$NB_USER/.ssh
COPY --chown=$NB_USER:$NB_GID ssh_keys/authorized_keys /home/$NB_USER/.ssh/authorized_keys
RUN chmod 600 /home/$NB_USER/.ssh/authorized_keys

# ==========================================
# PACKAGE INSTALLATION
# ==========================================

# STAGE 1: Install the build system tools first.
RUN python -m pip install --no-build-isolation -c /etc/pip/constraint.txt \
    scikit-build-core

# STAGE 2: Install all packages, ensuring the PyTorch trinity is installed together.
RUN python -m pip install --no-build-isolation -c /etc/pip/constraint.txt --upgrade \
    # --- The Holy Trinity ---
    torch \
    torchvision \
    torchaudio \
    # --- Key Libraries to Upgrade ---
    "diffusers==0.27.2" \
    transformers \
    # --- Build-from-Source ---
    "llama-cpp-python[server]" \
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
    parler-tts \
    huggingface_hub \
    datasets \
    "torchao==0.17.0" \
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
    mediapy==1.2.4 \
    moviepy==1.0.3 \
    nltk \
    openpyxl \
    pydub==0.25.1 \
    pytest \
    ydata-profiling \
    git+https://github.com/AbdullahO/mSSA.git@a7b25f5

# ==========================================
# JUPYTER CONFIGURATION
# ==========================================
RUN jupyter labextension enable jupyterlab-execute_time
RUN python -m ipykernel install --user --name=pytorch_modern --display-name="Python (Modern PyTorch)"
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
