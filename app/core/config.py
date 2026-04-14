"""Core settings facade.

This module provides the canonical import path for runtime settings while
remaining backward compatible with the previous location.
"""

from __future__ import annotations

from app.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
