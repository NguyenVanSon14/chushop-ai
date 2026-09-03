from typing import Any, Protocol

from app.modules.assistant.tools import ToolOutput


class BaseLLMProvider(Protocol):
    """Protocol for LLM Providers (Mock, OpenAI, Gemini, Groq, etc.)."""

    def process_question(
        self,
        question: str,
        execute_tool_fn: Any,
    ) -> tuple[ToolOutput, str]:
        """Given a question and a tool executor callback, determine intent/tool,

        execute tool via callback, and return (ToolOutput, explanation_text).
        """
        ...
