"""Path-safety helpers.

Every write performed by the generator must stay inside the project root.
``safe_join`` resolves a relative target against the root and refuses any
path that escapes it (``..`` traversal, absolute paths, symlink breakout).
"""

from __future__ import annotations

from pathlib import Path


class PathSafetyError(ValueError):
    """Raised when a target path would be written outside the project root."""


def safe_join(root: Path, relative: str) -> Path:
    """Resolve ``relative`` under ``root`` or raise :class:`PathSafetyError`.

    The returned path is absolute and guaranteed to live within ``root``.
    """
    root_resolved = root.resolve()
    if Path(relative).is_absolute():
        raise PathSafetyError(f"拒绝写入绝对路径：{relative}")

    candidate = (root_resolved / relative).resolve()
    # ``is_relative_to`` only exists on 3.9+, so compare prefixes manually.
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:  # pragma: no cover - exercised in tests
        raise PathSafetyError(
            f"拒绝写入项目根目录之外的路径：{relative}"
        ) from exc
    return candidate
