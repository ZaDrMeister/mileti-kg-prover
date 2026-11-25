"""LLM provider interface. No keys or SDKs yet.

The experiment needs a small local model and a strong API model.
Add one class per provider later, each with a `choose` method.
"""
from __future__ import annotations

from typing import Protocol


class Provider(Protocol):
    name: str

    def choose(self, prompt: str) -> str:
        """Return the model's reply: one rule application in the agreed format."""
        ...


class ScriptedProvider:
    """Plays back fixed replies. Used for tests and dry runs without a model."""

    name = "scripted"

    def __init__(self, replies: list[str]):
        self._replies = list(replies)

    def choose(self, prompt: str) -> str:
        if not self._replies:
            raise RuntimeError("ScriptedProvider ran out of replies")
        return self._replies.pop(0)
