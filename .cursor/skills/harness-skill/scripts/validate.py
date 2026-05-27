#!/usr/bin/env python3
"""Validate the Harness skill and/or a generated document set.

Two independent checks (run either or both):

  # Check the SKILL.md spec + bundled references
  python skills/harness-skill/scripts/validate.py --skill skills/harness-skill

  # Check a generated output tree (dead links, empty docs, {{placeholders}})
  python skills/harness-skill/scripts/validate.py --output ./my-project

Exit code is non-zero if any issue is found, so it doubles as a CI gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

_PLACEHOLDER_RE = re.compile(r"\{\{\s*[a-zA-Z0-9_]+\s*\}\}")
_LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

_SCANNED_SUFFIXES = {".md", ".mdc"}


def _frontmatter(text: str) -> dict:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def validate_skill(skill_dir: Path) -> List[str]:
    issues: List[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"缺少 SKILL.md：{skill_md}"]

    fields = _frontmatter(skill_md.read_text(encoding="utf-8"))
    name = fields.get("name", "")
    if not name:
        issues.append("frontmatter 缺少 name")
    elif name != skill_dir.name:
        issues.append(f"name（{name}）与目录名（{skill_dir.name}）不一致")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name or ""):
        issues.append(f"name 不符合命名规范（小写字母/数字/短横线）：{name!r}")
    if not fields.get("description"):
        issues.append("frontmatter 缺少 description")

    for ref in ("references/interview-response.schema.json", "references/runtime-compatibility.md"):
        if not (skill_dir / ref).exists():
            issues.append(f"引用资源缺失：{ref}")
    return issues


def _check_links(md_file: Path, root: Path) -> List[str]:
    issues: List[str] = []
    text = md_file.read_text(encoding="utf-8")
    for target in _LINK_RE.findall(text):
        target = target.strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        resolved = (md_file.parent / path_part).resolve()
        if not resolved.exists():
            rel = md_file.relative_to(root)
            issues.append(f"死链：{rel} -> {target}")
    return issues


def validate_output(root: Path) -> List[str]:
    issues: List[str] = []
    md_files = sorted(
        p for p in root.rglob("*") if p.suffix in _SCANNED_SUFFIXES and p.is_file()
    )
    if not md_files:
        return [f"未在 {root} 找到任何 Markdown 文档"]

    for md_file in md_files:
        text = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(root)
        if not text.strip():
            issues.append(f"空文档：{rel}")
        residue = _PLACEHOLDER_RE.findall(text)
        if residue:
            issues.append(f"占位符残留：{rel} -> {', '.join(sorted(set(residue)))}")
        issues.extend(_check_links(md_file, root))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate harness skill / output")
    parser.add_argument("--skill", help="Skill directory containing SKILL.md")
    parser.add_argument("--output", help="Generated output root to scan")
    args = parser.parse_args()

    if not args.skill and not args.output:
        parser.error("至少指定 --skill 或 --output 之一")

    all_issues: List[str] = []
    if args.skill:
        all_issues += validate_skill(Path(args.skill))
    if args.output:
        all_issues += validate_output(Path(args.output))

    if all_issues:
        print(f"发现 {len(all_issues)} 个问题：", file=sys.stderr)
        for issue in all_issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    print("校验通过：无死链、无空文档、无占位符残留。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
