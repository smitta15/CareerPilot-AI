"""
Centralized LLM handler with retry logic, fallback strategies,
and structured output support for CareerPilot AI.

Provides:
- Retry with exponential backoff
- Timeout handling
- Structured output with fallback
- Fallback to plain text parsing
- Comprehensive logging
"""

import json
import time
import random
from typing import Any, Dict, Optional, Type, TypeVar
from enum import Enum

from pydantic import BaseModel, ValidationError
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_core.exceptions import LangChainException

from app.logging_config import LoggerFactory
from app.settings import settings


logger = LoggerFactory.get_logger("careerpilot.llm")

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Base exception for LLM operations."""

    pass


class StructuredOutputError(LLMError):
    """Exception raised when structured output fails."""

    pass


class FallbackStrategy(Enum):
    """Strategy for handling LLM failures."""

    RETRY = "retry"
    FALLBACK_PLAIN_TEXT = "fallback_plain_text"
    FAIL = "fail"


class LLMHandler:
    """
    Centralized LLM handler with retry logic and fallback strategies.

    Handles:
    - Retries with exponential backoff and jitter
    - Structured output with schema validation
    - Fallback to plain text parsing
    - Timeout enforcement
    - Comprehensive logging
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        timeout: int = settings.LLM_TIMEOUT,
        max_retries: int = settings.LLM_RETRY_ATTEMPTS,
    ):
        """
        Initialize LLM handler.

        Args:
            model_name: Groq model name (defaults to GROQ_AGENT_MODEL)
            temperature: Model temperature for output randomness
            timeout: Timeout in seconds
            max_retries: Maximum retry attempts for failed operations
        """
        self.model_name = model_name or settings.GROQ_AGENT_MODEL
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries

        self._llm = ChatGroq(
            model=self.model_name,
            temperature=temperature,
            api_key=settings.GROQ_API_KEY,
        )

        logger.info(
            f"Initialized LLMHandler with model={self.model_name}, "
            f"temperature={temperature}, timeout={timeout}s, retries={max_retries}"
        )

    def get_llm(self) -> ChatGroq:
        """Get the underlying Groq LLM instance."""
        return self._llm

    def structured_output(
        self,
        output_schema: Type[T],
        prompt: str,
        fallback_strategy: FallbackStrategy = FallbackStrategy.FALLBACK_PLAIN_TEXT,
    ) -> T:
        """
        Generate structured output with retry and fallback.

        Args:
            output_schema: Pydantic model for output validation
            prompt: Prompt to send to LLM
            fallback_strategy: Strategy if structured output fails

        Returns:
            Validated instance of output_schema

        Raises:
            StructuredOutputError: If all retry attempts fail
            ValidationError: If response cannot be coerced to schema
        """
        logger.debug(f"Attempting structured output with schema={output_schema.__name__}")

        # Attempt 1: Structured output with tool calling
        for attempt in range(self.max_retries):
            try:
                with logger.timer(f"Structured output attempt {attempt + 1}"):
                    llm_with_schema = self._llm.with_structured_output(output_schema)
                    result = llm_with_schema.invoke(prompt, timeout=self.timeout)

                    # Validate result
                    if isinstance(result, dict):
                        result = output_schema(**result)
                    elif not isinstance(result, output_schema):
                        result = output_schema(**result.model_dump())

                    logger.info(
                        f"Structured output succeeded on attempt {attempt + 1} "
                        f"(schema={output_schema.__name__})"
                    )
                    return result

            except Exception as e:
                logger.warning(
                    f"Structured output attempt {attempt + 1} failed: {str(e)[:100]}"
                )

                if attempt < self.max_retries - 1:
                    wait_time = self._exponential_backoff(attempt)
                    logger.debug(f"Retrying after {wait_time:.2f}s...")
                    time.sleep(wait_time)

        # Fallback strategy
        if fallback_strategy == FallbackStrategy.FALLBACK_PLAIN_TEXT:
            logger.warning(
                f"Structured output failed after {self.max_retries} attempts; "
                f"falling back to plain text parsing"
            )
            return self._parse_plain_text(output_schema, prompt)

        elif fallback_strategy == FallbackStrategy.FAIL:
            raise StructuredOutputError(
                f"Structured output failed after {self.max_retries} attempts "
                f"for schema {output_schema.__name__}"
            )

        raise StructuredOutputError(
            f"Unknown fallback strategy: {fallback_strategy}"
        )

    def _parse_plain_text(self, output_schema: Type[T], prompt: str) -> T:
        """
        Parse plain text response and try to extract structured data.

        Args:
            output_schema: Target Pydantic schema
            prompt: Original prompt

        Returns:
            Instance of output_schema

        Raises:
            StructuredOutputError: If parsing fails completely
        """
        logger.debug("Parsing plain text response with field extraction")

        try:
            # Get plain text response
            response = self._llm.invoke(prompt, timeout=self.timeout)

            if isinstance(response, BaseMessage):
                text = response.content
            else:
                text = str(response)

            logger.debug(f"Plain text response (first 200 chars): {text[:200]}")

            # Try to extract JSON from response
            json_match = self._extract_json(text)
            if json_match:
                try:
                    data = json.loads(json_match)
                    result = output_schema(**data)
                    logger.info("Successfully parsed JSON from plain text response")
                    return result
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.warning(f"Failed to parse extracted JSON: {str(e)[:100]}")

            # Try to extract fields using regex patterns
            data = self._extract_fields_by_pattern(text, output_schema)
            if data:
                result = output_schema(**data)
                logger.info("Successfully extracted fields from plain text response")
                return result

            # Last resort: create minimal valid instance
            logger.warning("Falling back to minimal valid instance creation")
            return self._create_minimal_instance(output_schema)

        except Exception as e:
            raise StructuredOutputError(
                f"Plain text parsing failed: {str(e)}"
            ) from e

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON object from text (handles markdown code blocks)."""
        # Handle markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # Handle bare JSON objects
        for start in range(len(text)):
            if text[start] == "{":
                depth = 0
                for end in range(start, len(text)):
                    if text[end] == "{":
                        depth += 1
                    elif text[end] == "}":
                        depth -= 1
                        if depth == 0:
                            return text[start:end + 1]
                break

        return None

    def _extract_fields_by_pattern(
        self, text: str, schema: Type[BaseModel]
    ) -> Dict[str, Any]:
        """Try to extract fields using simple pattern matching."""
        import re

        data = {}
        schema_fields = schema.model_fields

        for field_name, field_info in schema_fields.items():
            # Try common patterns: "field: value", "field = value", "field: [...]"
            patterns = [
                f"{field_name}:\\s*(.+?)(?:\\n|$)",
                f"{field_name}\\s*=\\s*(.+?)(?:\\n|$)",
                f'"{field_name}"\\s*:\\s*(.+?)(?:,|' + r'\})',
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).strip()

                    # Type coercion
                    if field_info.annotation in (int, float):
                        try:
                            data[field_name] = float(value_str)
                            break
                        except ValueError:
                            pass
                    elif field_info.annotation == bool:
                        data[field_name] = value_str.lower() in ("true", "yes", "1")
                        break
                    elif field_info.annotation in (list, dict):
                        try:
                            data[field_name] = json.loads(value_str)
                            break
                        except json.JSONDecodeError:
                            pass
                    else:
                        data[field_name] = value_str
                        break

        return data

    def _create_minimal_instance(self, schema: Type[T]) -> T:
        """Create minimal valid instance of schema with defaults."""
        data = {}
        for field_name, field_info in schema.model_fields.items():
            if field_info.is_required():
                # Use field type defaults
                field_type = field_info.annotation
                if field_type == str:
                    data[field_name] = ""
                elif field_type in (int, float):
                    data[field_name] = 0
                elif field_type == bool:
                    data[field_name] = False
                elif field_type == list:
                    data[field_name] = []
                elif field_type == dict:
                    data[field_name] = {}
                else:
                    data[field_name] = None

        return schema(**data)

    def generate_text(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> str:
        """
        Generate plain text response with retry.

        Args:
            prompt: Prompt to send to LLM
            max_retries: Override default max_retries

        Returns:
            Generated text
        """
        max_attempts = max_retries or self.max_retries
        logger.debug(f"Generating text response (max_retries={max_attempts})")

        for attempt in range(max_attempts):
            try:
                with logger.timer(f"Text generation attempt {attempt + 1}"):
                    response = self._llm.invoke(prompt, timeout=self.timeout)

                    if isinstance(response, BaseMessage):
                        text = response.content
                    else:
                        text = str(response)

                    logger.info(f"Text generation succeeded on attempt {attempt + 1}")
                    return text

            except Exception as e:
                logger.warning(f"Text generation attempt {attempt + 1} failed: {str(e)[:100]}")

                if attempt < max_attempts - 1:
                    wait_time = self._exponential_backoff(attempt)
                    logger.debug(f"Retrying after {wait_time:.2f}s...")
                    time.sleep(wait_time)

        raise LLMError(
            f"Text generation failed after {max_attempts} attempts"
        )

    def _exponential_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Wait time in seconds
        """
        base_wait = settings.LLM_RETRY_BACKOFF ** attempt
        jitter = random.uniform(0, settings.LLM_RETRY_JITTER)
        wait_time = base_wait + jitter

        return min(wait_time, 30)  # Cap at 30 seconds


# ==================== Convenience Functions ====================


def create_handler(
    model: Optional[str] = None,
    temperature: float = 0.1,
    timeout: int = settings.LLM_TIMEOUT,
) -> LLMHandler:
    """Create an LLM handler with given configuration."""
    return LLMHandler(
        model_name=model,
        temperature=temperature,
        timeout=timeout,
    )


def get_planner_handler() -> LLMHandler:
    """Get LLM handler for planner agent."""
    return LLMHandler(
        model_name=settings.GROQ_PLANNER_MODEL,
        temperature=settings.LLM_TEMPERATURE_STRUCTURED,
    )


def get_agent_handler() -> LLMHandler:
    """Get LLM handler for general agents."""
    return LLMHandler(
        model_name=settings.GROQ_AGENT_MODEL,
        temperature=settings.LLM_TEMPERATURE_STRUCTURED,
    )


def get_report_handler() -> LLMHandler:
    """Get LLM handler for report agent."""
    return LLMHandler(
        model_name=settings.GROQ_REPORT_MODEL,
        temperature=settings.LLM_TEMPERATURE_STRUCTURED,
    )
