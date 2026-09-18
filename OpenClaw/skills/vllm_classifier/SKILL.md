---
name: vllm-vision-classifier
description: Offload image classification tasks to the local Qwen3-VL model on art.lan to save tokens.
requires:
  env:
    - VLLM_BASE_URL
---

# Local vLLM Vision Classification Skill

Use this skill when you need to categorize an image URL into specific types (e.g., Photograph, Drawing, Document, Painting) without consuming external API tokens.

## How to Run

To run a classification, execute the local python script:

```bash
python3 ~/.openclaw/skills/vllm-classifier/classifier.py "<IMAGE_URL>" "[OPTIONAL_COMMA_SEPARATED_CATEGORIES]"