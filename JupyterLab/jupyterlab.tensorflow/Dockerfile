# ----------------------------------------------------
# TENSORFLOW OPTIMIZED ENVIRONMENT
# ----------------------------------------------------
FROM nvcr.io/nvidia/tensorflow:24.12-tf2-py3

ARG NB_USER=jovyan
ARG NB_UID=1000
ARG NB_GID=1000

# 1. System Packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    libarchive-dev \
    python3.12-venv \
    && rm -rf /var/lib/apt/lists/*

# Create a symlink for the CUDA stub library so C++ packages can compile during Docker build
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 || true

# 2. User Setup
RUN if getent passwd $NB_UID; then userdel -r $(getent passwd $NB_UID | cut -d: -f1); fi && \
    if getent group $NB_GID; then groupdel $(getent group $NB_GID | cut -d: -f1); fi && \
    groupadd -g $NB_GID $NB_USER && \
    useradd -m -s /bin/bash -u $NB_UID -g $NB_GID $NB_USER && \
    echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$NB_USER && \
    chmod 0440 /etc/sudoers.d/$NB_USER && \
    git config --system credential.helper 'cache --timeout=34560000'

# 3. Virtual Environment (with access to NVIDIA's TensorFlow)
ENV VIRTUAL_ENV=/opt/jupyter_env
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV && \
    chown -R $NB_USER:$NB_GID $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
USER $NB_USER

# 4. Compile Llama-cpp (Using NVIDIA's build-time stub libraries)
RUN LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH \
    CMAKE_ARGS="-DGGML_CUDA=on" pip install --no-cache-dir "llama-cpp-python < 1"

# 5. Install Packages (Includes SciKeras, no PyTorch)
RUN pip install --no-cache-dir \
    "datasets < 5" \
    "kmedoids < 1" \
    "libarchive-c" \
    "matplotlib < 4" \
    "networkx < 4" \
    "numpy < 2" \
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
    "xgboost < 4" \
    "ydata-profiling < 5" \
    jupyterlab \
    jupyterlab_code_formatter \
    jupytext \
    jupyterlab_tensorboard_pro \
    notebook \
    ipywidgets \
    jupyterlab-git \
    jupyterlab_execute_time \
    ipykernel \
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

# Force Jupyter to enable the pre-built pip extension
RUN jupyter labextension enable jupyterlab-execute-time

# 6. Register Kernel
RUN python -m ipykernel install --user --name=jupyter_env_tf --display-name="Python (TensorFlow)"

# 7. Jupyter Configuration
RUN mkdir -p /opt/jupyter_env/share/jupyter/lab/settings
RUN echo '{\n\
  "@jupyterlab/notebook-extension:tracker": {\n\
    "recordTiming": true\n\
  }\n\
}' > /opt/jupyter_env/share/jupyter/lab/settings/overrides.json

WORKDIR /home/jovyan
EXPOSE 8888
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--notebook-dir=/home/jovyan"]