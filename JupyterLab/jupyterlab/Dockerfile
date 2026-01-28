FROM nvcr.io/nvidia/pytorch:25.12-py3

# 1. Install necessary system packages
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
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

# 5. Install Python dependencies (As jovyan)
RUN pip install --no-cache-dir \
    jupyterlab \
    jupyterlab_code_formatter \
    jupytext \
    jupyterlab_tensorboard_pro \
    notebook \
    torch \
    numpy \
    pandas \
    tensorflow \
    pytest \
    llama-cpp-python \
    datasets \
    matplotlib \
    seaborn \
    ipywidgets \
    jupyterlab-git \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib

# 6. Set the working directory
WORKDIR /home/jovyan

# 7. Git configuration
RUN git config --global credential.helper 'cache --timeout=36000'

# Expose Jupyter Lab port
EXPOSE 8888

# 8. Command to run Jupyter Lab
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0"]
