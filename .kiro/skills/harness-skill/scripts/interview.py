#!/usr/bin/env python3
"""Harness Skill interactive interview runner.

Usage:
  python skills/harness-skill/scripts/interview.py
  python skills/harness-skill/scripts/interview.py --resume
  python skills/harness-skill/scripts/interview.py --state-file .harness-skill-state.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


PHASES = [
    "projectExploration",
    "agentPersonality",
    "architecture",
    "prototypeSpecs",
]


def ask(prompt: str, required: bool = False, default: str | None = None) -> str:
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default is not None:
            value = default
        if required and not value:
            print("该字段必填，请重新输入。")
            continue
        return value


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    default_text = "y" if default else "n"
    while True:
        value = input(f"{prompt} [y/n, 默认 {default_text}]: ").strip().lower()
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("请输入 y 或 n。")


def ask_list(prompt: str, min_items: int = 1) -> List[str]:
    print(f"{prompt}（每行一项，输入空行结束）")
    items: List[str] = []
    while True:
        line = input("> ").strip()
        if not line:
            if len(items) < min_items:
                print(f"至少输入 {min_items} 项。")
                continue
            break
        items.append(line)
    return items


def load_state(state_file: Path) -> Dict[str, Any]:
    if not state_file.exists():
        return {
            "version": "0.1.0",
            "currentPhase": PHASES[0],
            "completedPhases": [],
            "responses": {},
        }
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("状态文件损坏，将从头开始。")
        return {
            "version": "0.1.0",
            "currentPhase": PHASES[0],
            "completedPhases": [],
            "responses": {},
        }


def save_state(state_file: Path, state: Dict[str, Any]) -> None:
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run_project_exploration(responses: Dict[str, Any]) -> None:
    print("\n=== Phase 1: Project Exploration ===")
    project_name = ask("项目名称", required=True)
    project_description = ask("项目描述", required=True)
    project_goals = ask_list("项目目标", min_items=1)
    success_criteria = ask_list("成功标准", min_items=1)

    target_users: List[Dict[str, Any]] = []
    while True:
        print("\n新增目标用户：")
        name = ask("用户类型名称", required=True)
        description = ask("用户描述", required=True)
        use_cases = ask_list("该用户的主要用例", min_items=1)
        target_users.append(
            {"name": name, "description": description, "primaryUseCases": use_cases}
        )
        if not ask_yes_no("继续添加目标用户？", default=False):
            break

    core_features: List[Dict[str, Any]] = []
    while True:
        print("\n新增核心功能：")
        name = ask("功能名称", required=True)
        description = ask("功能描述", required=True)
        priority = ask("优先级（high/medium/low）", default="medium").lower()
        if priority not in {"high", "medium", "low"}:
            priority = "medium"
        core_features.append(
            {"name": name, "description": description, "priority": priority}
        )
        if not ask_yes_no("继续添加核心功能？", default=False):
            break

    responses["projectExploration"] = {
        "projectName": project_name,
        "projectDescription": project_description,
        "projectGoals": project_goals,
        "successCriteria": success_criteria,
        "targetUsers": target_users,
        "coreFeatures": core_features,
    }


def run_agent_personality(responses: Dict[str, Any]) -> None:
    print("\n=== Phase 2: Agent Personality ===")
    voice_enabled = ask_yes_no("是否语音产品（需要 voice.md）？", default=False)
    personality: Dict[str, Any] = {"voiceEnabled": voice_enabled}
    if voice_enabled:
        personality["tone"] = ask(
            "语调（professional/friendly/casual/formal）", default="friendly"
        )
        personality["style"] = ask(
            "风格（concise/detailed/technical/accessible）", default="detailed"
        )
        formality = ask("正式程度（1-10）", default="5")
        try:
            personality["formality"] = max(1, min(10, int(formality)))
        except ValueError:
            personality["formality"] = 5
    responses["agentPersonality"] = personality


def run_architecture(responses: Dict[str, Any]) -> None:
    print("\n=== Phase 3: Architecture ===")
    languages = ask_list("编程语言", min_items=1)
    frameworks = ask_list("框架（前后端可混填）", min_items=1)
    databases = ask_list("数据库", min_items=1)
    architecture_pattern = ask(
        "架构模式（monolith/microservices/serverless/hybrid）", default="monolith"
    )
    if architecture_pattern not in {"monolith", "microservices", "serverless", "hybrid"}:
        architecture_pattern = "monolith"

    deployment = {
        "cloudProvider": ask("云服务商（可空）"),
        "containerization": ask("容器化（docker/kubernetes/none）", default="docker"),
        "cicdPlatform": ask("CI/CD 平台（可空）"),
    }
    if deployment["containerization"] not in {"docker", "kubernetes", "none"}:
        deployment["containerization"] = "docker"

    integrations: List[Dict[str, Any]] = []
    while ask_yes_no("是否添加第三方集成？", default=False):
        name = ask("集成名称", required=True)
        i_type = ask("类型（api/sdk/service）", default="api").lower()
        if i_type not in {"api", "sdk", "service"}:
            i_type = "api"
        purpose = ask("用途", required=True)
        integrations.append({"name": name, "type": i_type, "purpose": purpose})

    responses["architecture"] = {
        "techStack": {
            "languages": languages,
            "frameworks": frameworks,
            "databases": databases,
        },
        "architecturePattern": architecture_pattern,
        "deployment": deployment,
        "integrations": integrations,
    }


def run_prototype_specs(responses: Dict[str, Any]) -> None:
    print("\n=== Phase 4: Prototype Specs ===")
    output_format = ask("输出格式（html/markdown/wirescript）", default="markdown").lower()
    if output_format not in {"html", "markdown", "wirescript"}:
        output_format = "markdown"
    fidelity_level = ask("保真度（low/medium/high）", default="medium").lower()
    if fidelity_level not in {"low", "medium", "high"}:
        fidelity_level = "medium"

    prototype_specs: Dict[str, Any] = {
        "outputFormat": output_format,
        "fidelityLevel": fidelity_level,
        "componentStructure": {},
    }

    if output_format == "html":
        prototype_specs["cssFramework"] = ask(
            "CSS 框架（tailwind/bootstrap/custom）", default="tailwind"
        )
    elif output_format == "markdown":
        prototype_specs["docStyle"] = ask("文档风格", default="detailed")

    responses["prototypeSpecs"] = prototype_specs


def print_summary(responses: Dict[str, Any]) -> None:
    print("\n=== 访谈总结 ===")
    print(json.dumps(responses, ensure_ascii=False, indent=2))


def run_phase(phase: str, responses: Dict[str, Any]) -> None:
    if phase == "projectExploration":
        run_project_exploration(responses)
    elif phase == "agentPersonality":
        run_agent_personality(responses)
    elif phase == "architecture":
        run_architecture(responses)
    elif phase == "prototypeSpecs":
        run_prototype_specs(responses)


def next_phase(current: str) -> str | None:
    idx = PHASES.index(current)
    if idx + 1 >= len(PHASES):
        return None
    return PHASES[idx + 1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Skill interview runner")
    parser.add_argument(
        "--state-file",
        default=".harness-skill-state.json",
        help="Path of state file (default: .harness-skill-state.json)",
    )
    parser.add_argument(
        "--output",
        default="harness-interview-response.json",
        help="Final response JSON output path",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing state file if present",
    )
    args = parser.parse_args()

    state_file = Path(args.state_file)
    output_file = Path(args.output)

    if args.resume:
        state = load_state(state_file)
    else:
        if state_file.exists() and ask_yes_no("检测到已有状态，是否继续？", default=True):
            state = load_state(state_file)
        else:
            state = {
                "version": "0.1.0",
                "currentPhase": PHASES[0],
                "completedPhases": [],
                "responses": {},
            }
            if state_file.exists():
                state_file.unlink()

    responses: Dict[str, Any] = state.get("responses", {})
    current_phase = state.get("currentPhase", PHASES[0])

    while current_phase is not None:
        try:
            run_phase(current_phase, responses)
            if current_phase not in state["completedPhases"]:
                state["completedPhases"].append(current_phase)
            current_phase = next_phase(current_phase)
            state["currentPhase"] = current_phase or "summary"
            state["responses"] = responses
            save_state(state_file, state)
        except KeyboardInterrupt:
            state["responses"] = responses
            state["currentPhase"] = current_phase
            save_state(state_file, state)
            print(f"\n已保存中断状态到: {state_file}")
            return 130

    print_summary(responses)
    if not ask_yes_no("确认输出并结束访谈？", default=True):
        print("未确认，状态已保留，可后续继续。")
        return 1

    output_file.write_text(
        json.dumps(responses, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if state_file.exists():
        state_file.unlink()
    print(f"访谈完成，结果已写入: {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
