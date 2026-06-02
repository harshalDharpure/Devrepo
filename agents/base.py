from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from backend.config import settings
from shared.schemas import AgentName


class AdkExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentDescriptor:
    name: AgentName
    instruction: str
    model: str = settings.gemini_model
    output_schema: type | dict[str, Any] | None = None

    def to_adk_agent(self) -> Any | None:
        """Return a Google ADK LlmAgent when google-adk is installed."""
        try:
            from google.adk.agents import Agent
        except ImportError:
            return None
        return Agent(
            name=self.name.value,
            description=self.instruction,
            model=self.model,
            instruction=self.instruction,
            output_schema=self.output_schema,
            mode="single_turn",
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )


class DomainAgent:
    descriptor: AgentDescriptor

    @property
    def adk_agent(self) -> Any | None:
        return self.descriptor.to_adk_agent()

    @property
    def adk_enabled(self) -> bool:
        return not settings.demo_mode

    async def run_adk_json(self, prompt: str) -> dict[str, Any]:
        if not self.adk_enabled:
            raise AdkExecutionError("ADK execution is disabled in demo mode.")

        adk_agent = self.adk_agent
        if adk_agent is None:
            raise AdkExecutionError("google-adk is not installed.")

        try:
            from google.adk.runners import InMemoryRunner
            from google.genai import types
        except ImportError as exc:
            raise AdkExecutionError("Google ADK runtime dependencies are unavailable.") from exc

        app_name = "venturepilot"
        user_id = "venturepilot-workflow"
        session_id = f"{self.descriptor.name.value}-session"
        runner = InMemoryRunner(agent=adk_agent, app_name=app_name)
        await runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )

        final_payload: Any | None = None
        final_text = ""
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message,
            ):
                if event.output is not None:
                    final_payload = event.output
                if event.content and event.content.parts:
                    final_text = "".join(
                        getattr(part, "text", "") or ""
                        for part in event.content.parts
                    ) or final_text
                if event.is_final_response():
                    if event.output is not None:
                        final_payload = event.output
                    if event.content and event.content.parts:
                        final_text = "".join(
                            getattr(part, "text", "") or ""
                            for part in event.content.parts
                        ) or final_text
        except Exception as exc:
            raise AdkExecutionError(str(exc)) from exc
        finally:
            close = getattr(runner, "close", None)
            if close is not None:
                maybe_awaitable = close()
                if hasattr(maybe_awaitable, "__await__"):
                    await maybe_awaitable

        if isinstance(final_payload, dict):
            return final_payload
        if hasattr(final_payload, "model_dump"):
            return final_payload.model_dump()
        if final_text:
            return self._parse_json_text(final_text)
        raise AdkExecutionError("ADK agent did not return JSON output.")

    def _parse_json_text(self, text: str) -> dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise AdkExecutionError("ADK response did not contain a JSON object.")
            return json.loads(match.group(0))
