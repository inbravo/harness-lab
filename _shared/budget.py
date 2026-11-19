"""BudgetEnforcer — context manager capping step count, wall-clock time, and estimated token cost."""
__author__ = "Amit Dixit"

import time
from dataclasses import dataclass, field

# Cost proxy — $0 real cost on Ollama, useful for relative comparisons and cloud porting.
COST_PER_PROMPT_TOKEN = 0.000_003      # $3 / 1M tokens (GPT-4o equivalent proxy)
COST_PER_COMPLETION_TOKEN = 0.000_015  # $15 / 1M tokens


class BudgetExceeded(Exception):
    pass


@dataclass
class BudgetEnforcer:
    max_steps: int = 25
    max_seconds: float = 300.0
    max_cost_usd: float = 0.50

    _steps: int = field(default=0, init=False)
    _start: float = field(default=0.0, init=False)
    _cost: float = field(default=0.0, init=False)

    def __enter__(self) -> "BudgetEnforcer":
        self._start = time.monotonic()
        return self

    def __exit__(self, *_) -> None:
        pass

    def tick(self, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        self._steps += 1
        self._cost += (
            prompt_tokens * COST_PER_PROMPT_TOKEN
            + completion_tokens * COST_PER_COMPLETION_TOKEN
        )
        elapsed = time.monotonic() - self._start

        if self._steps > self.max_steps:
            raise BudgetExceeded(f"step cap reached: {self._steps} > {self.max_steps}")
        if elapsed > self.max_seconds:
            raise BudgetExceeded(f"time cap reached: {elapsed:.1f}s > {self.max_seconds}s")
        if self._cost > self.max_cost_usd:
            raise BudgetExceeded(f"cost cap reached: ${self._cost:.4f} > ${self.max_cost_usd}")

    @property
    def summary(self) -> dict:
        return {
            "steps": self._steps,
            "elapsed_s": round(time.monotonic() - self._start, 2),
            "estimated_cost_usd": round(self._cost, 6),
        }
