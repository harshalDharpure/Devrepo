from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.config import settings
from shared.schemas import AgentName


@dataclass(frozen=True)
class AgentDescriptor:
    name: AgentName
    instruction: str
    model: str = settings.gemini_model

    def to_adk_agent(self) -> Any | None:
        """Return a Google ADK Agent when google-adk is installed.

        The workflow owns routing; ADK is used here as the agent runtime boundary
        for deployments that enable live Gemini/Vertex execution.
        """
        try:
            from google.adk.agents import Agent
        except ImportError:
            return None
        return Agent(name=self.name.value, model=self.model, instruction=self.instruction)


class DomainAgent:
    descriptor: AgentDescriptor

    @property
    def adk_agent(self) -> Any | None:
        return self.descriptor.to_adk_agent()

