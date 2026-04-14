"""Core database facade.

This module centralizes SQLAlchemy primitives used by routers/services and keeps
compatibility with the existing `app.database` implementation.
"""

from __future__ import annotations

from app.database import Base, SessionLocal, engine, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
