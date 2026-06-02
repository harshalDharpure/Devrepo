from __future__ import annotations

import json
import re
from typing import Any

from backend.config import Settings, settings


class LLMUnavailableError(RuntimeError):
    pass


class GeminiClient:
    """Small wrapper around Google Gen AI with graceful demo-mode fallback."""

    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self._client: Any | None = None

    @property
    def enabled(self) -> bool:
        if self.config.demo_mode:
            return False
        if self.config.google_genai_use_vertexai:
            return bool(self.config.google_cloud_project)
        return bool(self.config.google_api_key)

    def _load_client(self) -> Any:
        if not self.enabled:
            raise LLMUnavailableError("Gemini client is disabled in demo mode or missing credentials.")
        if self._client is not None:
            return self._client

        try:
            from google import genai
            from google.genai.types import HttpOptions
        except ImportError as exc:
            raise LLMUnavailableError("Install google-genai to use Gemini or Vertex AI.") from exc

        if self.config.google_genai_use_vertexai:
            self._client = genai.Client(
                vertexai=True,
                project=self.config.google_cloud_project,
                location=self.config.google_cloud_location,
                http_options=HttpOptions(api_version="v1"),
            )
        else:
            self._client = genai.Client(api_key=self.config.google_api_key)
        return self._client

    async def generate_text(self, prompt: str) -> str:
        client = self._load_client()
        response = client.models.generate_content(
            model=self.config.gemini_model,
            contents=prompt,
        )
        return getattr(response, "text", "") or ""

    async def generate_json(self, prompt: str) -> dict[str, Any]:
        text = await self.generate_text(prompt)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

