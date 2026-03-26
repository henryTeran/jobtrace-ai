"""Logging utilities with optional ANSI colors."""

from __future__ import annotations

import logging
import sys


class ColorFormatter(logging.Formatter):
    """Simple ANSI color formatter by log level."""

    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        if not color:
            return base
        return f"{color}{base}{self.RESET}"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger once for the entire application."""

    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = ColorFormatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(handler)
