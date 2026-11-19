"""
tracer.py — JSONL span tracer for harness-lab step-level observability.

Writes one JSONL line per span when TRACE=1. Each line carries span_id,
parent_id, name, start_ms, duration_ms, and any key/value pairs set via
span.set(). Set TRACE_DIR to redirect output from the default "traces/" folder.

Usage:
    TRACE=1 python pipeline.py
    # → traces/s1-fixed-pipeline.jsonl

    from _shared.tracer import Tracer
    tracer = Tracer("my-run")
    with tracer.span("step_name") as span:
        span.set("tool", "search_logs")
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

# ── config ────────────────────────────────────────────
TRACING_ENABLED = os.getenv("TRACE", "0") == "1"
TRACE_DIR       = Path(os.getenv("TRACE_DIR", "traces"))


# ── span ──────────────────────────────────────────────

@dataclass
class Span:
    """Single timed unit of work. Call set() to attach metadata before it closes."""

    span_id:      str        = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id:    str | None = None
    name:         str        = ""
    start_ns:     int        = field(default_factory=time.time_ns)
    _data:        dict       = field(default_factory=dict)
    _output_path: Path       = field(default=Path("/dev/null"))

    def set(self, key: str, value: Any) -> None:
        """Attach a key/value pair to this span's JSONL record.

        Args:
            key:   Field name in the output record.
            value: JSON-serialisable value.
        """
        self._data[key] = value

    def _write(self, end_ns: int) -> None:
        if not TRACING_ENABLED:
            return
        record = {
            "span_id":     self.span_id,
            "parent_id":   self.parent_id,
            "name":        self.name,
            "start_ms":    self.start_ns // 1_000_000,
            "duration_ms": (end_ns - self.start_ns) // 1_000_000,
            **self._data,
        }
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._output_path.open("a") as f:
            f.write(json.dumps(record) + "\n")


# ── tracer ────────────────────────────────────────────

class Tracer:
    """Root tracer bound to a single run. Each run gets its own JSONL file."""

    def __init__(self, run_id: str = "") -> None:
        self.run_id      = run_id or uuid.uuid4().hex[:8]
        self.output_path = TRACE_DIR / f"{self.run_id}.jsonl"

    @contextmanager
    def span(self, name: str, parent_id: str | None = None) -> Generator[Span, None, None]:
        """Context manager that yields a Span and writes it on exit.

        Args:
            name:      Human-readable label for this span.
            parent_id: Optional parent span_id for nested tracing.

        Yields:
            Span instance for attaching metadata.
        """
        s = Span(name=name, parent_id=parent_id, _output_path=self.output_path)
        try:
            yield s
        finally:
            s._write(time.time_ns())
