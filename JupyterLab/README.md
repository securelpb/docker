# Dual-GPU-Accelerated JupyterLab Workstation

This repository contains JupyterLab architecture optimized for a single NVIDIA RTX 3090. It can support multiple Docker containers while sharing a single workspace, persistent IDE settings, and a unified Hugging Face model cache.

---

## **Directory Structure**

For this architecture to build correctly, your project folder should look exactly like this:

```text
/your-project-root
│
├── docker-compose.yml
├── nginx/
│   └── default.conf
├── jupyterlab/
│   └── Dockerfile
└── jupyterlab.pytorch/ # Optional additional environments
    └── Dockerfile
```

---

## **1. Nginx Configuration**
**File:** `nginx/default.conf`
**Purpose:** Routes traffic, handles long-running kernel web sockets, and allows massive 2GB file uploads.
 * SERVER 1: TensorFlow Environment (Port 8888)

---

## **2. Docker Compose**
**File:** `docker-compose.yml`
**Purpose:** Orchestrates the containers, mounts the shared volumes (keeping the workspace clean and caching HuggingFace models), and attaches the RTX 3090 GPU.
* Pulls **JUPYTER_TOKEN** from environment variable, which should be set in the `.env` file. 

---

## **3. Hybrid Environment**
**File:** `jupyterlab/Dockerfile`
**Purpose:** Hybrid PyTorch/TensorFlow environment. Uses CUDA stubs for building `llama-cpp-python` and includes TensorFlow's "polite" memory growth environmental variable so it doesn't hoard the GPU.
 * Based on nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04
 * Built for 8.6 CUDA Compute Capability
 * Held back to "numpy < 2", "torch==2.4.0", "torchvision==0.19.0", and "torchaudio==2.4.0" for compatibility with dgl-cu124 (last release).


---

## **4. PyTorch Environment** (retired)
**File:** `jupyterlab.pytorch/Dockerfile`
**Purpose:** Pure PyTorch environment. Avoids NumPy 2.0 and OpenCV conflicts, matches the host CUDA driver, and correctly compiles C++ hardware bindings for the RTX 3090.
 * Based on nvidia/cuda:12.6.2-cudnn-devel-ubuntu24.04
 * Built for 8.6 CUDA Compute Capability
