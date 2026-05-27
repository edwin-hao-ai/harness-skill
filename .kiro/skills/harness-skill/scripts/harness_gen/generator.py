"""Generation orchestrator.

Drives the frozen :data:`plan.PLAN` to turn an :class:`InterviewResponse`
into the v1 document set, progressively and safely:

- ``harness-map.md`` is written first so it is always a usable navigation
  entry even if a later document fails (Requirement 15).
- whole-file docs are created if absent; existing ones are skipped unless
  ``force=True`` (Constraint: never overwrite without confirmation).
- entry files are merged as managed blocks, preserving user content.
- a failure on one document is recorded but does not delete or roll back
  documents already written (Requirement 19, partial-output preservation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from . import managed_block
from .context import build_context
from .model import InterviewResponse
from .paths import safe_join
from .plan import MANAGED_BLOCK, DocSpec, docs_for
from .template import render

DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "templates"

_LAYER_TITLES = [
    ("platform", "Platform Layer"),
    ("domain", "Domain Layer"),
    ("application", "Application Layer"),
    ("interface", "Interface Layer"),
    ("memory", "Memory Layer"),
    ("entry", "Agent Entry Points"),
]

ProgressFn = Callable[[str], None]


@dataclass(frozen=True)
class GenerationResult:
    created: Tuple[str, ...] = ()
    updated: Tuple[str, ...] = ()
    skipped: Tuple[str, ...] = ()
    failed: Tuple[Tuple[str, str], ...] = ()  # (target, error message)

    @property
    def ok(self) -> bool:
        return not self.failed


@dataclass
class _Accumulator:
    created: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    failed: List[Tuple[str, str]] = field(default_factory=list)

    def freeze(self) -> GenerationResult:
        return GenerationResult(
            created=tuple(self.created),
            updated=tuple(self.updated),
            skipped=tuple(self.skipped),
            failed=tuple(self.failed),
        )


def _load_template(templates_dir: Path, name: str) -> str:
    path = templates_dir / name
    if not path.exists():
        raise FileNotFoundError(f"模板缺失：{path}")
    return path.read_text(encoding="utf-8")


def _harness_map_sections(specs: Tuple[DocSpec, ...]) -> str:
    """Build the layer-grouped TOC body for harness-map.md."""
    blocks: List[str] = []
    for layer_key, layer_title in _LAYER_TITLES:
        layer_docs = sorted(
            (s for s in specs if s.layer == layer_key), key=lambda s: s.target
        )
        if not layer_docs:
            continue
        lines = [f"## {layer_title}", ""]
        lines += [f"- [{s.title}]({s.target}) — {s.description}" for s in layer_docs]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _write_whole_file(
    root: Path, spec: DocSpec, content: str, force: bool, acc: _Accumulator
) -> None:
    target = safe_join(root, spec.target)
    if target.exists() and not force:
        acc.skipped.append(spec.target)
        return
    existed = target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    (acc.updated if existed else acc.created).append(spec.target)


def _write_managed(
    root: Path,
    spec: DocSpec,
    body: str,
    templates_dir: Path,
    acc: _Accumulator,
) -> None:
    target = safe_join(root, spec.target)
    existing = target.read_text(encoding="utf-8") if target.exists() else None
    prefix = ""
    if spec.prefix_template:
        prefix = _load_template(templates_dir, spec.prefix_template)
    merged = managed_block.merge(existing, body.strip(), prefix_if_new=prefix)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(merged, encoding="utf-8")
    (acc.updated if existing is not None else acc.created).append(spec.target)


def generate(
    response: InterviewResponse,
    root: Path,
    templates_dir: Path = DEFAULT_TEMPLATES_DIR,
    force: bool = False,
    progress: ProgressFn = lambda _msg: None,
) -> GenerationResult:
    """Generate the v1 Harness document set under ``root``."""
    specs = docs_for(response)
    context: Dict[str, str] = build_context(response)
    context["harness_map_sections"] = _harness_map_sections(specs)

    acc = _Accumulator()
    for spec in specs:
        try:
            template_text = _load_template(templates_dir, spec.template)
            content = render(template_text, context)
            if spec.kind == MANAGED_BLOCK:
                _write_managed(root, spec, content, templates_dir, acc)
            else:
                _write_whole_file(root, spec, content, force, acc)
            progress(f"✓ {spec.target}")
        except Exception as exc:  # noqa: BLE001 - report, preserve prior output
            acc.failed.append((spec.target, str(exc)))
            progress(f"✗ {spec.target} — {exc}")

    return acc.freeze()
