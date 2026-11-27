
import os
import requests

from dotenv import load_dotenv

load_dotenv()


class OllamaClient:

    def __init__(self, model=None):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        )

        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:3b"
        )

        self.timeout = int(
            os.getenv("REQUEST_TIMEOUT", "120")
        )

    def generate(self, prompt: str, model=None) -> str:
        selected_model = model or self.model

        url = f"{self.base_url}/api/chat"

        payload = {
            "model": selected_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]["content"]

    def health_check(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )

            response.raise_for_status()
            return True

        except requests.RequestException:
            return False
