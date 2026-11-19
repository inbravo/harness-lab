"""
budget.py — BudgetEnforcer context manager for harness-lab step loops.

Caps three dimensions simultaneously: step count, wall-clock time, and an
estimated token cost (proxy only — Ollama has no real cost, but the value is
useful for relative comparisons and cloud-porting exercises).

Usage:
    from _shared.budget import BudgetEnforcer, BudgetExceeded
    with BudgetEnforcer(max_steps=25) as budget:
        for step in range(100):
            budget.tick(prompt_tokens=pt, completion_tokens=ct)
    print(budget.summary)
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import time
from dataclasses import dataclass, field

# ── cost proxy ────────────────────────────────────────
# $0 real cost on Ollama; useful for relative comparisons and cloud porting.
COST_PER_PROMPT_TOKEN      = 0.000_003   # $3 / 1M tokens (GPT-4o equivalent proxy)
COST_PER_COMPLETION_TOKEN  = 0.000_015   # $15 / 1M tokens


# ── exceptions ────────────────────────────────────────

class BudgetExceeded(Exception):
    """Raised when any budget dimension is exceeded."""


# ── enforcer ─────────────────────────────────────────

@dataclass
class BudgetEnforcer:
    """Context manager that enforces step, time, and cost caps on an agent loop.

    Args:
        max_steps:    Maximum number of loop iterations before raising BudgetExceeded.
        max_seconds:  Wall-clock time cap in seconds.
        max_cost_usd: Estimated token cost cap in USD (proxy; not a real charge on Ollama).
    """

    max_steps:    int   = 25
    max_seconds:  float = 300.0
    max_cost_usd: float = 0.50

    _steps: int   = field(default=0,   init=False)
    _start: float = field(default=0.0, init=False)
    _cost:  float = field(default=0.0, init=False)

    def __enter__(self) -> BudgetEnforcer:
        self._start = time.monotonic()
        return self

    def __exit__(self, *_) -> None:
        pass

    def tick(self, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        """Record one step and accumulate token cost; raise BudgetExceeded if any cap is hit.

        Args:
            prompt_tokens:     Tokens consumed in the prompt for this step.
            completion_tokens: Tokens produced in the completion for this step.

        Raises:
            BudgetExceeded: When steps, elapsed time, or estimated cost exceeds its cap.
        """
        self._steps += 1
        self._cost  += (
            prompt_tokens     * COST_PER_PROMPT_TOKEN
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
        """Return a snapshot of steps, elapsed time, and estimated cost.

        Returns:
            Dict with keys: steps, elapsed_s, estimated_cost_usd.
        """
        return {
            "steps":               self._steps,
            "elapsed_s":           round(time.monotonic() - self._start, 2),
            "estimated_cost_usd":  round(self._cost, 6),
        }
