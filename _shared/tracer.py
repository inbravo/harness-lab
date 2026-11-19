"""JSONL span tracer. Writes one line per step when TRACE=1. TRACE_DIR sets output folder."""
__author__ = "Amit Dixit"

import json
import os
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

TRACING_ENABLED = os.getenv("TRACE", "0") == "1"
TRACE_DIR = Path(os.getenv("TRACE_DIR", "traces"))


@dataclass
class Span:
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id: str | None = None
    name: str = ""
    start_ns: int = field(default_factory=time.time_ns)
    _data: dict = field(default_factory=dict)
    _output_path: Path = field(default=Path("/dev/null"))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def _write(self, end_ns: int) -> None:
        if not TRACING_ENABLED:
            return
        record = {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_ms": self.start_ns // 1_000_000,
            "duration_ms": (end_ns - self.start_ns) // 1_000_000,
            **self._data,
        }
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._output_path.open("a") as f:
            f.write(json.dumps(record) + "\n")


class Tracer:
    def __init__(self, run_id: str = "") -> None:
        self.run_id = run_id or uuid.uuid4().hex[:8]
        self.output_path = TRACE_DIR / f"{self.run_id}.jsonl"

    @contextmanager
    def span(self, name: str, parent_id: str | None = None) -> Generator[Span, None, None]:
        s = Span(name=name, parent_id=parent_id, _output_path=self.output_path)
        try:
            yield s
        finally:
            s._write(time.time_ns())
