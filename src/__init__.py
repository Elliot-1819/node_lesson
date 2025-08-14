"""Lesson Builder package root.

This package contains the modular pipeline, services, and utilities
for transforming raw sections into interactive lesson steps.

Architecture is intentionally decomposed to make each step
testable and observable in isolation.
"""

__all__ = [
    "config",
    "services",
    "utils",
]

__version__ = "0.1.0"


