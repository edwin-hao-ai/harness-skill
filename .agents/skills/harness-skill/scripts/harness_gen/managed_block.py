"""Idempotent managed-block merging for agent entry files.

Entry files (``AGENTS.md``, ``CLAUDE.md``, ``.cursor/rules/harness.mdc``)
may already contain content the user wrote by hand. We never overwrite the
whole file: instead we maintain a single delimited block and only ever
touch the text between the markers.

    <!-- HARNESS:START -->
    ...harness-managed content...
    <!-- HARNESS:END -->

Running a merge twice with the same body produces byte-identical output, so
re-generation never duplicates the block.
"""

from __future__ import annotations

import re
from typing import Optional

START_MARKER = "<!-- HARNESS:START -->"
END_MARKER = "<!-- HARNESS:END -->"

_BLOCK_RE = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)


def _canonical_block(body: str) -> str:
    """Wrap ``body`` in markers with normalized surrounding whitespace."""
    return f"{START_MARKER}\n{body.strip()}\n{END_MARKER}"


def has_block(text: str) -> bool:
    """True if ``text`` already contains a harness managed block."""
    return bool(_BLOCK_RE.search(text))


def merge(existing: Optional[str], body: str, prefix_if_new: str = "") -> str:
    """Return file content with the harness block set to ``body``.

    - ``existing is None`` → create the file (optionally led by
      ``prefix_if_new``, used to seed e.g. ``.mdc`` frontmatter).
    - existing file *with* a block → replace the block in place.
    - existing file *without* a block → append the block, preserving all
      pre-existing content untouched.

    The operation is idempotent: feeding the output back in with the same
    ``body`` yields the same output.
    """
    block = _canonical_block(body)

    if existing is None:
        prefix = ""
        if prefix_if_new:
            prefix = prefix_if_new.rstrip() + "\n\n"
        return f"{prefix}{block}\n"

    if has_block(existing):
        return _BLOCK_RE.sub(lambda _m: block, existing, count=1)

    return f"{existing.rstrip()}\n\n{block}\n"
