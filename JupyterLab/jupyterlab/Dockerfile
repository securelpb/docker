FROM nvcr.io/nvidia/pytorch:24.12-py3

# Define ARGs early so they can be used across multiple stages
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. Install necessary system packages (Run all root commands together)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    libarchive-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Handle User Creation & Permissions
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    # OPTIMIZATION: Grant passwordless sudo to jovyan so the 'sudo' package is actually usable
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER && \
    # OPTIMIZATION: Moved git config here to group root operations and save layers
    git config --system credential.helper 'cache --timeout=34560000'

# 3. Setup the Virtual Environment
ENV VIRTUAL_ENV=/opt/jupyter_env
RUN python3 -m venv $VIRTUAL_ENV && \
    chown -R $NB_USER:$NB_GID $VIRTUAL_ENV

# Set path to use the venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

FROM nvcr.io/nvidia/pytorch:24.12-py3

# Define ARGs early so they can be used across multiple stages
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. Install necessary system packages (Run all root commands together)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    libarchive-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Handle User Creation & Permissions
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    # OPTIMIZATION: Grant passwordless sudo to jovyan so the 'sudo' package is actually usable
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER && \
    # OPTIMIZATION: Moved git config here to group root operations and save layers
    git config --system credential.helper 'cache --timeout=34560000'

# 3. Setup the Virtual Environment
ENV VIRTUAL_ENV=/opt/jupyter_env
RUN python3 -m venv $VIRTUAL_ENV && \
    chown -R $NB_USER:$NB_GID $VIRTUAL_ENV

# Set path to use the venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 4. Switch to the user 'jovyan'
USER $NB_USER

# 5. FIRST: Install the library that requires source compilation.
# We do this first so it gets cached heavily. It takes the longest to build.
RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install --no-cache-dir "llama-cpp-python < 1"

# 6. SECOND: Install ALL other packages in a single command.
# This ensures pip looks at ALL interdependencies globally and resolves them correctly.
# NOTE: Removed torch, torchvision, and torchaudio because the Nvidia base image
# already provides highly optimized, pre-installed versions of these!
RUN pip install --no-cache-dir \
    # Heavy Data Science
    "datasets < 5" \
    "kmedoids < 1" \
    "libarchive-c" \
    "matplotlib < 4" \
    "networkx < 4" \
    "numpy == 2.0.2" \
    "openpyxl < 4" \
    "pandas < 4" \
    "pmdarima >= 2.1.0" \
    "scikeras < 1" \
    "scikit-image < 1" \
    "scikit-learn < 2" \
    scikit-learn-extra \
    "scipy < 2" \
    "seaborn < 1" \
    "sklearn-compat < 1" \
    "sklearn-pandas < 3" \
    "statsmodels < 1" \
    "tensorflow < 3" \
    "xgboost < 4" \
    "ydata-profiling < 5" \
    # JupyterLab & IDE Tools
    jupyterlab \
    jupyterlab_code_formatter \
    jupytext \
    jupyterlab_tensorboard_pro \
    notebook \
    ipywidgets \
    jupyterlab-git \
    jupyterlab_execute_time \
    # APIs and Utilities
    "beautifulsoup4 < 5" \
    "Flask < 4" \
    Faker \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    "huggingface_hub < 2" \
    "huggingface_hub[cli] < 2" \
    "kneed < 1" \
    "opencv-contrib-python < 5" \
    "opencv-python < 5" \
    "opencv-python-headless < 5" \
    "plotly < 7" \
    "pytest < 10" \
    "decorator < 6" \
    "nbformat < 6" \
    "shap < 1"

# Create the JupyterLab settings directory
RUN mkdir -p /opt/jupyter_env/share/jupyter/lab/settings

# Create the overrides.json file to enable cell execution timing by default
RUN echo '{\n\
  "@jupyterlab/notebook-extension:tracker": {\n\
    "recordTiming": true\n\
  }\n\
}' > /opt/jupyter_env/share/jupyter/lab/settings/overrides.json

# 8. Set the working directory
WORKDIR /home/jovyan

# Expose Jupyter Lab port
EXPOSE 8888

# 9. Command to run Jupyter Lab
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]
RUN mkdir -p /opt/jupyter_env/share/jupyter/lab/settings

# Create the overrides.json file to enable cell execution timing by default
RUN echo '{\n\
  "@jupyterlab/notebook-extension:tracker": {\n\
    "recordTiming": true\n\
  }\n\
}' > /opt/jupyter_env/share/jupyter/lab/settings/overrides.json

# 8. Set the working directory
WORKDIR /home/jovyan

# Expose Jupyter Lab port
EXPOSE 8888

# 9. Command to run Jupyter Lab
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]