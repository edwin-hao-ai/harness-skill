"""Minimal, dependency-free template engine.

Templates use ``{{ key }}`` placeholders. The context is a flat mapping of
fully-rendered strings (see :mod:`context`), so the engine never has to
implement loops or conditionals — those are resolved when the context is
built. This keeps rendering deterministic and trivially testable.
"""

from __future__ import annotations

import re
from typing import List, Mapping

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


class TemplateError(ValueError):
    """Raised when a template references a key absent from the context."""


def render(template: str, context: Mapping[str, str]) -> str:
    """Substitute every ``{{ key }}`` in ``template`` using ``context``.

    Raises :class:`TemplateError` if a referenced key is missing, so an
    incomplete context fails loudly rather than emitting a half-filled doc.
    """
    missing: List[str] = []

    def _replace(match: "re.Match[str]") -> str:
        key = match.group(1)
        if key not in context:
            missing.append(key)
            return match.group(0)
        return str(context[key])

    result = _PLACEHOLDER.sub(_replace, template)
    if missing:
        unique = ", ".join(sorted(set(missing)))
        raise TemplateError(f"模板缺少上下文键：{unique}")
    return result


def find_residual_placeholders(text: str) -> List[str]:
    """Return any ``{{ key }}`` tokens still present in ``text``."""
    return [match.group(0) for match in _PLACEHOLDER.finditer(text)]
