"""Harness document generator package.

Turns a validated interview response (see
``references/interview-response.schema.json``) into the v1 Harness
Engineering documentation set described in ``specs/harness-skill/tasks.md``.

The package is intentionally dependency-free (Python 3.8+ stdlib only) so it
runs identically across every target runtime (Kiro, Cursor, Codex, Claude
Code, OpenClaw, Hermes).
"""

from .model import InterviewResponse
from .generator import GenerationResult, generate

__all__ = ["InterviewResponse", "GenerationResult", "generate"]
