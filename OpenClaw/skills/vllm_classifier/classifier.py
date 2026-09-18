# classifier.py
import os
import sys
import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI, OpenAIError

logging.basicConfig(level=logging.ERROR)

class VLLMVisionClassifierSkill:
    DEFAULT_MODEL = "cyankiwi/Qwen3-VL-8B-Instruct-AWQ-4bit"
    DEFAULT_CATEGORIES = ["Photograph", "Painting", "Drawing", "Document"]

    def __init__(self):
        self.base_url = os.getenv("VLLM_BASE_URL", "http://art.lan:8000/v1")
        self.api_key = os.getenv("VLLM_API_KEY", "EMPTY")
        self.model_name = os.getenv("VLLM_MODEL_NAME", self.DEFAULT_MODEL)

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def classify(self, image_url: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        target_categories = categories or self.DEFAULT_CATEGORIES
        categories_str = ", ".join(target_categories)

        prompt = (
            f"Classify this image as exactly one of the following categories: [{categories_str}]. "
            f"Provide a brief explanation, then state the final classification clearly."
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=256
            )

            message_obj = response.choices[0].message
            content = getattr(message_obj, "content", "")
            reasoning = getattr(message_obj, "reasoning", None) or getattr(message_obj, "reasoning_content", None)

            return {
                "success": True,
                "result": content.strip() if content else None,
                "reasoning": reasoning.strip() if reasoning else None,
                "model": response.model
            }
        except OpenAIError as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # CLI entry point for OpenClaw process execution
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image URL provided."}))
        sys.exit(1)

    url = sys.argv[1]
    cats = sys.argv[2].split(",") if len(sys.argv) > 2 else None

    skill = VLLMVisionClassifierSkill()
    res = skill.classify(image_url=url, categories=cats)
    print(json.dumps(res))