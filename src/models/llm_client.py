import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import requests


class ModelClient(ABC):
    def __init__(self, model_id: str, vendor: str, temperature: float = 0.0,
                 max_tokens: int = 1024, timeout: int = 120) -> None:
        self.model_id = model_id
        self.vendor = vendor
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @abstractmethod
    def _call(self, prompt: str, system: str | None) -> str:
        ...

    def complete(self, prompt: str, system: str | None = None,
                 max_retries: int = 5) -> tuple[str, dict]:
        last_error = ""
        for attempt in range(max_retries):
            try:
                text = self._call(prompt, system)
                return text, self._meta()
            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else 0
                if status == 429 or status >= 500:
                    last_error = f"HTTP {status}"
                    time.sleep(min(2 ** attempt, 30))
                    continue
                raise
            except requests.RequestException as exc:
                last_error = str(exc)
                time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"request failed after {max_retries} attempts: {last_error}")

    def _meta(self) -> dict[str, Any]:
        return {
            "vendor": self.vendor,
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "run_date_utc": datetime.now(timezone.utc).isoformat(),
        }


class OpenAIClient(ModelClient):
    API_URL = "https://api.openai.com/v1/chat/completions"

    def _call(self, prompt: str, system: str | None) -> str:
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        messages = ([{"role": "system", "content": system}] if system else [])
        messages.append({"role": "user", "content": prompt})
        response = requests.post(
            self.API_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": self.model_id,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


class AnthropicClient(ModelClient):
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def _call(self, prompt: str, system: str | None) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        response = requests.post(
            self.API_URL,
            headers={"x-api-key": key, "anthropic-version": self.API_VERSION},
            json={
                "model": self.model_id,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system or "",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return "".join(
            block.get("text", "") for block in response.json()["content"]
            if block.get("type") == "text"
        )


class GoogleClient(ModelClient):
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def _call(self, prompt: str, system: str | None) -> str:
        key = os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY not set")
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        response = requests.post(
            self.API_URL.format(model=self.model_id),
            headers={"x-goog-api-key": key},
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        candidates = response.json().get("candidates", [])
        if not candidates:
            return ""
        blocks = candidates[0].get("content", {}).get("parts", [])
        return "".join(block.get("text", "") for block in blocks)


class MockClient(ModelClient):
    def __init__(self, model_id: str = "mock-model", vendor: str = "mock",
                 canned: str = "MOCK RESPONSE: Example answer.") -> None:
        super().__init__(model_id, vendor)
        self.canned = canned

    def _call(self, prompt: str, system: str | None) -> str:
        return self.canned


def build_client(spec: str, temperature: float = 0.0,
                 max_tokens: int = 1024) -> ModelClient:
    vendor_by_prefix = {
        "gpt-": "openai",
        "o1": "openai",
        "o3": "openai",
        "claude-": "anthropic",
        "gemini-": "google",
    }
    vendor = next((v for p, v in vendor_by_prefix.items() if spec.startswith(p)), "mock")
    clients = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "google": GoogleClient,
    }
    client_cls = clients.get(vendor, MockClient)
    return client_cls(spec, vendor, temperature=temperature, max_tokens=max_tokens)
