# Use an NVIDIA CUDA 12.9 base image for Ubuntu 24.04
FROM nvcr.io/nvidia/pytorch:25.09-py3

# Install necessary packages and Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for JupyterLab
RUN python3 -m venv /opt/jupyter_env

# Activate the virtual environment and install JupyterLab
ENV PATH="/opt/jupyter_env/bin:$PATH"
RUN pip install jupyterlab jupyterlab_code_formatter jupytext jupyterlab_tensorboard_pro notebook

# Set the working directory
WORKDIR /home/jovyan

# Expose Jupyter Lab port
EXPOSE 8888

# Command to run Jupyter Lab
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--allow-root", "--ip=0.0.0.0"]
