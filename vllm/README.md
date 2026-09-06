# vLLM Server with Docker Compose
## Management
Restart with `docker compose --profile gemma12b up -d --force-recreate`
Switch profiles with `docker stop vllm-gemma12b && docker rm vllm-gemma12b` and then run the restart.

To add a new model:
```yaml
  vllm-qwen25-vl: <-- Update this
    <<: *vllm-common
    container_name: vllm-qwen-vl <-- Update this
    profiles: [ "qwen-vl" ] <-- Update this, and this is the name you use at the CLI
    command: >
      python3 -m vllm.entrypoints.openai.api_server
      --model Qwen/Qwen2.5-VL-7B-Instruct <-- Update this, and tune arguments below.
```

To see the names of the models being servered
```bash
curl http://art.lan:8000/v1/models -H "Authorization: Bearer VLLM_API_KEY" | jq '.models[] | .name'
```