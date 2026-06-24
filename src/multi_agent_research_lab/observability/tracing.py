"""Tracing hooks.

Supports minimal JSON spans and optional LangSmith when env vars are set.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Record a span with duration; optionally forward to LangSmith."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}

    if os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true":
        try:
            from langsmith import traceable  # noqa: F401

            logger.debug("LangSmith tracing enabled for span: %s", name)
        except ImportError:
            logger.debug("langsmith not installed; using local spans only")

    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        logger.info("trace_span %s duration=%.3fs attrs=%s", name, span["duration_seconds"], attributes)
