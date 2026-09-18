# Llama.cpp Server with Docker Compose

Welcome, primate, to your personal `llama.cpp` server setup. This document is your map through this part of the digital jungle. Don't worry, I've used small words.

## Overview

This setup uses Docker Compose to run the `llama.cpp` server, which is designed to serve GGUF (Georgi Gerganov Universal Format) models. It's separate from the vLLM setup and is managed by the `docker-compose.yml` file in this directory.

The key difference: `llama.cpp` is simple. It doesn't auto-download models. You have to manually download the `.gguf` files and tell the server exactly which file to load.

---

## Structure of `docker-compose.yml`

The Compose file is organized to be easy to manage, even for a monkey.

### `x-llama-common`

This is a reusable template (a YAML anchor, if you want to sound smart) that defines all the common settings for any `llama.cpp` service we run.

- **`image`**: Uses `ghcr.io/ggml-org/llama.cpp:server-cuda`, the official image with NVIDIA GPU support. This image has `llama-server` as its entrypoint, so the `command` section should only contain arguments.
- **`ports`**: Maps port `8081` on your host machine to port `8080` inside the container. This is to avoid conflicts with your vLLM server, which uses port 8000.
- **`volumes`**: This is the important part. It maps a local directory on your server (`/home/alex/docker_server_data/llama_cpp_models`) to the `/models` directory inside the container. **This is where you must place your downloaded `.gguf` files.**
- **`deploy`**: Ensures the container has access to all of your NVIDIA GPUs.

### `services`

This section defines the individual model profiles. Each service is a self-contained configuration for running a specific model.

- **`<<: *llama-common`**: This line magically inherits all the settings from the `x-llama-common` template.
- **`container_name`**: A unique, human-readable name for the running container.
- **`profiles`**: A unique name for the service that you use in the `docker-compose up` command.
- **`command`**: This is the most critical part. It provides the **arguments** to the `llama-server` entrypoint.
  - `-m /models/your-model-name.gguf`: Specifies the **exact filename** of the model to load from the `/models` volume.
  - `--n-gpu-layers 99`: Offloads as many layers as possible to the GPU.
  - `--ctx-size 131000`: Sets the context size. You can adjust this based on your needs and VRAM.
  - `--flash-attn on`: Optimize attention calculations.

---

## How to Add a New Model

Follow these steps. Do not skip any, or your server will throw a tantrum.

1.  **Download the Model**: Go to Hugging Face and find a model you like in GGUF format. Download the `.gguf` file to your computer. I recommend a `Q4_K_M` or `Q5_K_M` quantization for a good balance of performance and quality.

2.  **Place the Model**: Move the downloaded `.gguf` file into the `device` directory specified in the `volumes` section of your `docker-compose.yml`. For you, that is:
    `/home/alex/docker_server_data/llama_cpp_models/`

3.  **Update Docker Compose**:
    a. Open the `docker-compose.yml` file.
    b. Copy an existing service block (e.g., `llama-gemma-agentic`).
    c. Paste it below the existing service.
    d. Change the service name (e.g., `llama-mixtral-instruct`).
    e. Update the `container_name` to be unique.
    f. Update the `profiles` name to be unique (e.g., `["mixtral-instruct"]`).
    g. **Most Importantly**: Update the `command` section with the arguments for the new model, ensuring the `-m` flag points to the **exact filename** of the new model you just downloaded.

    **Example:**
    ```yaml
    # ... existing services ...

    llama-mixtral-instruct:
      <<: *llama-common
      container_name: llama-mixtral-instruct
      profiles: ["mixtral-instruct"]
      command: >
        -m /models/mixtral-8x7b-instruct-v0.1.Q5_K_M.gguf
        --host 0.0.0.0
        --port 8080
        -ngl 99
        -c 16384
    ```

---

## How to Run a Service

After you've added and configured your new model profile:

1.  Open a terminal on your Docker server.
2.  Navigate to the directory containing this `docker-compose.yml` file.
3.  Run the following command, replacing `<profile-name>` with the profile you want to run:

    ```sh
    docker compose --profile <profile-name> up -d --force-recreate
    ```

    For example, to run the Gemma model you configured:
    ```sh
    docker compose --profile gemma-agentic up -d --force-recreate
    ```

4.  The server will start. You can access its web interface or API endpoint at `http://<your-server-ip>:8081`.

Now, go play with your new toys. And try not to break anything.
