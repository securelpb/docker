FROM nvcr.io/nvidia/pytorch:24.12-py3

# 1. Install necessary system packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    libarchive-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Handle User Creation (Fixed Order: Delete User -> Delete Group -> Create New)
ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# Logic:
# 1. Check if a USER exists with UID 1000. If so, delete the user first (this frees the group).
# 2. Check if a GROUP exists with GID 1000. If so, delete it.
# 3. Create the new jovyan user and group.
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER

# 3. Setup the Virtual Environment
ENV VIRTUAL_ENV=/opt/jupyter_env
RUN python3 -m venv $VIRTUAL_ENV && \
    chown -R $NB_USER:$NB_GID $VIRTUAL_ENV

# Set path to use the venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 4. Switch to the user 'jovyan'
USER $NB_USER

RUN pip install --no-cache-dir \
    "datasets < 5" \
    "kmedoids < 1" \
    "libarchive-c" \
    "matplotlib < 4" \
    "networkx < 4" \
    "numpy == 2.0.2" \
    "openpyxl < 4" \
    "pandas < 4" \
    "pmdarima >= 2.1.0" \
    "scikit-image < 1" \
    "scikit-learn < 2" \
    scikit-learn-extra \
    "scipy < 2" \
    "seaborn < 1" \
    "sklearn-compat < 1" \
    "sklearn-pandas < 3" \
    "statsmodels < 1" \
    "tensorflow < 3" \
    "torch < 3" \
    "torchaudio < 3" \
    "torchvision < 1" \
    "xgboost < 4"

# 5. Install the library that requires source compilation.
# This is separated so that changes in the packages above or below 
# don't trigger a slow CUDA re-compile of this package.
RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install --no-cache-dir "llama-cpp-python < 1"

# 6. Install JupyterLab and IDE tools.
# You might add or remove extensions here frequently.
RUN pip install --no-cache-dir \
    jupyterlab \
    jupyterlab_code_formatter \
    jupytext \
    jupyterlab_tensorboard_pro \
    notebook \
    ipywidgets \
    jupyterlab-git

# 7. Install lightweight API and utility libraries.
# These change most often as you update your code.
RUN pip install --no-cache-dir \
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

# 8. Set the working directory
WORKDIR /home/jovyan

# 9. Git configuration
USER root
RUN git config --system credential.helper 'cache --timeout=34560000'
USER $NB_USER

# Expose Jupyter Lab port
EXPOSE 8888

# 10. Command to run Jupyter Lab
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]
