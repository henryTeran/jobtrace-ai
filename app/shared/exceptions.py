"""Domain-level exceptions used across modules."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for expected business/domain errors."""


class ValidationError(DomainError):
    """Raised when client input is semantically invalid."""


class IntegrationError(DomainError):
    """Raised when an external integration fails."""
