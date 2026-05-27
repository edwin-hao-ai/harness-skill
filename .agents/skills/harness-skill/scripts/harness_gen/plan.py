"""The frozen v1 generation plan.

Declares every document the generator emits, in the progressive order
required by ``specs/harness-skill/requirements.md`` Requirement 15:
``harness-map`` first, then each layer, then the agent entry points.

Two kinds of output:

- ``whole_file`` docs are fully harness-owned (created if absent, skipped or
  overwritten on re-run depending on ``--force``).
- ``managed_block`` entry files are merged via :mod:`managed_block`, so any
  user-authored content around the block is preserved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from .model import InterviewResponse

WHOLE_FILE = "whole_file"
MANAGED_BLOCK = "managed_block"


@dataclass(frozen=True)
class DocSpec:
    layer: str
    template: str  # filename under assets/templates/
    target: str  # path relative to project root
    title: str  # human label for harness-map / progress
    description: str  # one-line description for harness-map
    kind: str = WHOLE_FILE
    condition: Optional[Callable[[InterviewResponse], bool]] = None
    prefix_template: Optional[str] = None  # frontmatter seed for new .mdc files

    def included(self, response: InterviewResponse) -> bool:
        return self.condition is None or self.condition(response)


def _voice_enabled(response: InterviewResponse) -> bool:
    return response.personality.voice_enabled


# Order matters: harness-map first, layers next, entry points last.
PLAN: Tuple[DocSpec, ...] = (
    DocSpec(
        layer="index",
        template="harness-map.md.tmpl",
        target="harness-map.md",
        title="Harness Map",
        description="中央导航索引，指向所有 Harness 文档。",
    ),
    DocSpec(
        layer="platform",
        template="platform/spec.md.tmpl",
        target="harness/platform/spec.md",
        title="Spec",
        description="产品需求：问题、目标/非目标、用户、功能、成功标准。",
    ),
    DocSpec(
        layer="platform",
        template="platform/design.md.tmpl",
        target="harness/platform/design.md",
        title="Design Doc",
        description="工程设计文档（Google 风格）：约束实现，记录决策、约束程度与备选方案。",
    ),
    DocSpec(
        layer="platform",
        template="platform/architecture.md.tmpl",
        target="harness/platform/architecture.md",
        title="Architecture",
        description="落定后的架构参考：技术栈、组件、数据模型、部署、集成。",
    ),
    DocSpec(
        layer="platform",
        template="platform/voice.md.tmpl",
        target="harness/platform/voice.md",
        title="Voice",
        description="语音交互规范（仅语音产品生成）。",
        condition=_voice_enabled,
    ),
    DocSpec(
        layer="domain",
        template="domain/use-cases.md.tmpl",
        target="harness/domain/use-cases.md",
        title="Use Cases",
        description="按核心功能展开的用例与主流程。",
    ),
    DocSpec(
        layer="application",
        template="application/project-structure.md.tmpl",
        target="harness/application/project-structure.md",
        title="Project Structure",
        description="基于架构模式的目录结构与组织约定。",
    ),
    DocSpec(
        layer="interface",
        template="interface/user-guide.md.tmpl",
        target="harness/interface/user-guide.md",
        title="User Guide",
        description="面向目标用户的使用说明。",
    ),
    DocSpec(
        layer="memory",
        template="memory/memory.md.tmpl",
        target="memory/memory.md",
        title="Memory Index",
        description="记忆系统索引，指向 decisions 与 patterns。",
    ),
    DocSpec(
        layer="memory",
        template="memory/decisions.md.tmpl",
        target="memory/decisions.md",
        title="Decisions",
        description="访谈中确定的架构与设计决策。",
    ),
    DocSpec(
        layer="entry",
        template="AGENTS.md.tmpl",
        target="AGENTS.md",
        title="AGENTS.md",
        description="通用 Agent 入口（managed block）。",
        kind=MANAGED_BLOCK,
    ),
    DocSpec(
        layer="entry",
        template="CLAUDE.md.tmpl",
        target="CLAUDE.md",
        title="CLAUDE.md",
        description="Claude Code 入口（managed block）。",
        kind=MANAGED_BLOCK,
    ),
    DocSpec(
        layer="entry",
        template="cursor-rules.mdc.tmpl",
        target=".cursor/rules/harness.mdc",
        title=".cursor/rules/harness.mdc",
        description="Cursor 规则入口（managed block）。",
        kind=MANAGED_BLOCK,
        prefix_template="cursor-rules.prefix.tmpl",
    ),
)


def docs_for(response: InterviewResponse) -> Tuple[DocSpec, ...]:
    """Return the subset of the plan applicable to ``response``."""
    return tuple(spec for spec in PLAN if spec.included(response))
