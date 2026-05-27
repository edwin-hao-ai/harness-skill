#!/usr/bin/env python3
"""Generate the Harness v1 document set from an interview response.

Usage:
  python skills/harness-skill/scripts/generate.py
  python skills/harness-skill/scripts/generate.py --response harness-interview-response.json
  python skills/harness-skill/scripts/generate.py --root . --force

This is the deterministic, testable path. The agent-led chat flow (see
``references/agent-interview-protocol.md``) produces the same document set;
this script lets the same templates be exercised without a live agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running both as a module and as a bare script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_gen import generate  # noqa: E402
from harness_gen.generator import DEFAULT_TEMPLATES_DIR  # noqa: E402
from harness_gen.model import InterviewResponse, ResponseError  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness v1 document generator")
    parser.add_argument(
        "--response",
        default="harness-interview-response.json",
        help="Interview response JSON (default: harness-interview-response.json)",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root to generate into (default: current directory)",
    )
    parser.add_argument(
        "--templates",
        default=str(DEFAULT_TEMPLATES_DIR),
        help="Template directory (default: bundled assets/templates)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing whole-file documents (default: skip them)",
    )
    parser.add_argument(
        "--keep-state",
        action="store_true",
        help="Keep .harness-skill-state.json after a successful run",
    )
    args = parser.parse_args()

    response_path = Path(args.response)
    if not response_path.exists():
        print(f"找不到响应文件：{response_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(response_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"响应文件不是合法 JSON：{exc}", file=sys.stderr)
        return 2

    try:
        response = InterviewResponse.from_dict(data)
    except ResponseError as exc:
        print(f"响应内容不合法：{exc}", file=sys.stderr)
        return 2

    root = Path(args.root)
    result = generate(
        response,
        root=root,
        templates_dir=Path(args.templates),
        force=args.force,
        progress=print,
    )

    print("\n=== 生成结果 ===")
    print(f"新建 {len(result.created)} · 更新 {len(result.updated)} · 跳过 {len(result.skipped)} · 失败 {len(result.failed)}")
    for target in result.skipped:
        print(f"  跳过（已存在，使用 --force 覆盖）：{target}")
    for target, message in result.failed:
        print(f"  失败：{target} — {message}", file=sys.stderr)

    if not result.ok:
        print("\n部分文档生成失败，已保留成功生成的文档，可修复后重试。", file=sys.stderr)
        return 1

    state_file = root / ".harness-skill-state.json"
    if state_file.exists() and not args.keep_state:
        state_file.unlink()
        print(f"已清理访谈状态文件：{state_file}")

    print("完成。先看 harness-map.md。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
