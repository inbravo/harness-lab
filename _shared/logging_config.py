"""
logging_config.py — Shared logging setup for harness-lab.

Log file : ../logs/harness-lab.log  (RotatingFileHandler, 5 MB × 3 backups)
File     : DEBUG and above  (every detail, including tool calls and step traces)
Console  : INFO and above   (key events only — not noisy during normal runs)

All loggers are named under the "harness" hierarchy so they can be tuned or
silenced together without touching the root logger.

Usage in any module:
    import logging_config, logging
    logging_config.setup()
    log = logging.getLogger("harness.<module>")
"""
# ─────────────────────────────────────────────────────
# Author   : Amit Dixit
# GitHub   : https://github.com/inbravo
# Web      : https://inbravo.github.io
# LinkedIn : https://www.linkedin.com/in/inbravo/
# ─────────────────────────────────────────────────────

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "logs" / "harness-lab.log"

_configured = False


def setup() -> None:
    """Configure the 'harness' logger hierarchy. Safe to call multiple times."""
    global _configured
    if _configured:
        return
    _configured = True

    LOG_FILE.parent.mkdir(exist_ok=True)

    root = logging.getLogger("harness")
    if root.handlers:
        return
    root.setLevel(logging.DEBUG)

    file_fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)-36s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_fmt = logging.Formatter("%(levelname)-8s  %(name)s  %(message)s")

    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(file_fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(console_fmt)

    root.addHandler(fh)
    root.addHandler(ch)
