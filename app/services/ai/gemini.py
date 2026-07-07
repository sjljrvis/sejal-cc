"""
Supervity AI Service - Base class for AI integration

Wraps the google-genai SDK (>=1.51.0) with Gemini 3 defaults.

Single source of truth for:
  - Client initialization (reads GEMINI_API_KEY)
  - Model selection (reads AI_MODEL, default gemini-3-flash-preview)
  - thinking_config (reads AI_THINKING_LEVEL, default medium)
  - GenerateContentConfig builders (text, json, structured, with-tools)

Subclasses (PolicyService, InsightsService, ChatService, RuleArchitect)
should call _get_*_config() instead of constructing config inline so the
Gemini 3 fields (thinking_config, response_json_schema, etc.) are applied
consistently.

Gemini 3 notes (vs the 2.x code this replaces):
  - No explicit `temperature` is set anywhere by default. Gemini 3's default
    of 1.0 is recommended; low values cause looping on complex tasks.
  - `thinking_budget` is replaced by `thinking_config.thinking_level`
    (minimal | low | medium | high).
  - For function calling, the SDK preserves `thought_signature` automatically
    when you append the full `candidate.content` to history. Do NOT
    reconstruct content from text-only or you'll get HTTP 400 on the next turn.
"""

import os
import logging
from typing import Optional, Type

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Valid thinking levels per Gemini 3 docs.
_VALID_THINKING_LEVELS = {"minimal", "low", "medium", "high"}


class GeminiService:
    """
    Base class for Supervity AI integration.

    Holds the genai client + model + thinking_level configuration that all
    subclasses share. Subclasses should compose config via the helpers below.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("AI_MODEL", "gemini-3-flash-preview")
        self.fallback_model = os.getenv("AI_FALLBACK_MODEL") or None
        self.thinking_level = self._read_thinking_level("AI_THINKING_LEVEL", "medium")
        self.client = None

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info(
                    f"Supervity AI client initialized "
                    f"(model={self.model}, thinking_level={self.thinking_level})"
                )
            except ImportError:
                logger.warning(
                    "google-genai package not installed (pip install 'google-genai>=1.51.0'). "
                    "Supervity AI features will use mock responses."
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GEMINI_API_KEY not set. Supervity AI features will use mock responses.")

    @property
    def is_available(self) -> bool:
        return self.client is not None

    @staticmethod
    def _read_thinking_level(env_var: str, default: str) -> str:
        raw = (os.getenv(env_var) or default).strip().lower()
        if raw not in _VALID_THINKING_LEVELS:
            logger.warning(
                f"{env_var}={raw!r} is not one of {_VALID_THINKING_LEVELS}. Falling back to {default!r}."
            )
            return default
        return raw

    def _thinking_config(self, level: Optional[str] = None):
        """Build a ThinkingConfig for the given (or default) level."""
        try:
            from google.genai import types
        except ImportError:
            return None
        chosen = (level or self.thinking_level).lower()
        if chosen not in _VALID_THINKING_LEVELS:
            chosen = self.thinking_level
        return types.ThinkingConfig(thinking_level=chosen)

    def _get_text_config(
        self,
        system_instruction: Optional[str] = None,
        thinking_level: Optional[str] = None,
        tools=None,
    ):
        """Config for free-text / chat output."""
        try:
            from google.genai import types
        except ImportError:
            return None
        kwargs = {"thinking_config": self._thinking_config(thinking_level)}
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        if tools is not None:
            kwargs["tools"] = tools
        return types.GenerateContentConfig(**kwargs)

    def _get_json_config(
        self,
        system_instruction: Optional[str] = None,
        thinking_level: Optional[str] = None,
    ):
        """Config for unstructured JSON output (no schema)."""
        try:
            from google.genai import types
        except ImportError:
            return None
        kwargs = {
            "response_mime_type": "application/json",
            "thinking_config": self._thinking_config(thinking_level),
        }
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        return types.GenerateContentConfig(**kwargs)

    def _get_structured_config(
        self,
        schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        thinking_level: Optional[str] = None,
    ):
        """Config for schema-validated JSON output via Pydantic."""
        try:
            from google.genai import types
        except ImportError:
            return None
        kwargs = {
            "response_mime_type": "application/json",
            "response_json_schema": schema.model_json_schema(),
            "thinking_config": self._thinking_config(thinking_level),
        }
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        return types.GenerateContentConfig(**kwargs)
