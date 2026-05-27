"""Build the flat template context from an :class:`InterviewResponse`.

Every value here is a fully-rendered Markdown string. Optional interview
fields fall back to sensible defaults so a sparse response still produces a
complete, placeholder-free document set.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, Sequence

from .model import (
    Architecture,
    Feature,
    InterviewResponse,
    PrototypeSpecs,
    TargetUser,
    TechStack,
)

_PRIORITY_LABEL = {"high": "高", "medium": "中", "low": "低"}
_PATTERN_LABEL = {
    "monolith": "单体应用 (Monolith)",
    "microservices": "微服务 (Microservices)",
    "serverless": "无服务器 (Serverless)",
    "hybrid": "混合架构 (Hybrid)",
}


def _bullet_list(items: Sequence[str], empty: str = "_（待补充）_") -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def _comma(items: Sequence[str], empty: str = "未指定") -> str:
    return "、".join(items) if items else empty


def _features_table(features: Sequence[Feature]) -> str:
    header = "| 功能 | 优先级 | 说明 |\n| --- | --- | --- |"
    rows = [
        f"| {f.name} | {_PRIORITY_LABEL.get(f.priority, f.priority)} | {f.description} |"
        for f in features
    ]
    return "\n".join([header, *rows])


def _users_sections(users: Sequence[TargetUser]) -> str:
    blocks = []
    for user in users:
        cases = _bullet_list(user.primary_use_cases)
        blocks.append(f"### {user.name}\n\n{user.description}\n\n**主要用例：**\n\n{cases}")
    return "\n\n".join(blocks)


def _use_cases_sections(users: Sequence[TargetUser], features: Sequence[Feature]) -> str:
    """One use-case section per core feature (Req 10 use-case mapping)."""
    actor = users[0].name if users else "用户"
    blocks = []
    for index, feature in enumerate(features, start=1):
        blocks.append(
            f"### UC-{index:02d}: {feature.name}\n\n"
            f"- **优先级**：{_PRIORITY_LABEL.get(feature.priority, feature.priority)}\n"
            f"- **主要角色**：{actor}\n"
            f"- **目标**：{feature.description}\n"
            f"- **主流程**：\n"
            f"  1. {actor} 发起「{feature.name}」操作\n"
            f"  2. 系统校验输入并执行核心逻辑\n"
            f"  3. 系统返回结果并记录状态"
        )
    return "\n\n".join(blocks)


def _tech_stack_table(stack: TechStack) -> str:
    header = "| 维度 | 选型 |\n| --- | --- |"
    rows = [
        f"| 编程语言 | {_comma(stack.languages)} |",
        f"| 框架 | {_comma(stack.frameworks)} |",
        f"| 数据库 | {_comma(stack.databases)} |",
    ]
    return "\n".join([header, *rows])


def _deployment_summary(arch: Architecture) -> str:
    dep = arch.deployment
    return (
        f"- **云服务商**：{dep.cloud_provider or '未指定'}\n"
        f"- **容器化**：{dep.containerization or 'none'}\n"
        f"- **CI/CD**：{dep.cicd_platform or '未指定'}"
    )


def _integrations_block(arch: Architecture) -> str:
    if not arch.integrations:
        return "_无第三方集成。_"
    header = "| 名称 | 类型 | 用途 |\n| --- | --- | --- |"
    rows = [f"| {i.name} | {i.type} | {i.purpose} |" for i in arch.integrations]
    return "\n".join([header, *rows])


def _structure_tree(arch: Architecture) -> str:
    """Project tree derived from the chosen architecture pattern."""
    common = (
        "project-root/\n"
        "├── src/            # 源代码\n"
        "├── tests/          # 测试\n"
        "├── docs/           # 文档\n"
    )
    pattern = arch.architecture_pattern
    if pattern == "microservices":
        body = (
            "project-root/\n"
            "├── services/      # 各微服务（独立部署单元）\n"
            "│   ├── service-a/\n"
            "│   └── service-b/\n"
            "├── libs/          # 共享库\n"
            "├── gateway/       # API 网关\n"
            "└── deploy/        # 编排与部署清单\n"
        )
    elif pattern == "serverless":
        body = (
            "project-root/\n"
            "├── functions/     # 各函数入口\n"
            "├── lib/           # 共享逻辑\n"
            "├── events/        # 事件/触发器定义\n"
            "└── infra/         # IaC 配置\n"
        )
    elif pattern == "hybrid":
        body = common + "├── services/      # 拆分出的独立服务\n└── deploy/        # 部署清单\n"
    else:  # monolith
        body = common + "└── deploy/        # 部署清单\n"
    return body


def build_context(response: InterviewResponse) -> Dict[str, str]:
    project = response.project
    arch = response.architecture
    proto: PrototypeSpecs = response.prototype
    personality = response.personality

    proto_options = (
        f"CSS 框架：{proto.css_framework or 'tailwind'}"
        if proto.output_format == "html"
        else f"文档风格：{proto.doc_style or 'detailed'}"
    )

    return {
        "project_name": project.project_name,
        "project_description": project.project_description,
        "generated_at": date.today().isoformat(),
        "project_goals_list": _bullet_list(project.project_goals),
        "success_criteria_list": _bullet_list(
            project.success_criteria, empty="_（未定义成功标准）_"
        ),
        "target_users_sections": _users_sections(project.target_users),
        "target_users_names": _comma([u.name for u in project.target_users]),
        "core_features_table": _features_table(project.core_features),
        "core_features_count": str(len(project.core_features)),
        "use_cases_sections": _use_cases_sections(
            project.target_users, project.core_features
        ),
        "architecture_pattern": _PATTERN_LABEL.get(
            arch.architecture_pattern, arch.architecture_pattern
        ),
        "tech_stack_table": _tech_stack_table(arch.tech_stack),
        "languages": _comma(arch.tech_stack.languages),
        "frameworks": _comma(arch.tech_stack.frameworks),
        "databases": _comma(arch.tech_stack.databases),
        "deployment_summary": _deployment_summary(arch),
        "integrations_block": _integrations_block(arch),
        "project_structure_tree": _structure_tree(arch),
        "output_format": proto.output_format,
        "fidelity_level": proto.fidelity_level,
        "prototype_options": proto_options,
        "voice_enabled": "是" if personality.voice_enabled else "否",
        "agent_tone": personality.tone or "friendly",
        "agent_style": personality.style or "detailed",
    }
