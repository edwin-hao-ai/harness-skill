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
    DesignSystem,
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
_ELEVATION_LABEL = {
    "shadows": "通过阴影（box-shadow）传达层级，层级越高阴影越深。",
    "tonal-layers": "通过色调分层传达层级，避免重阴影，背景与卡片使用微妙的色差区分。",
    "flat": "扁平化设计，通过边框与颜色对比区分层级，不使用阴影。",
}
_SHAPES_LABEL = {
    "sharp": "直角设计语言，所有交互元素与容器使用 0-2px 圆角，传达精准、工程化的美感。",
    "rounded": "圆角设计语言，按钮与卡片使用 8-12px 圆角，兼顾现代感与亲和力。",
    "organic": "有机形态设计，大圆角（16px+）与不规则形状，传达温暖、友好的品牌个性。",
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


def _design_context(design: DesignSystem, project_name: str) -> Dict[str, str]:
    """Build all design-system related context keys for design.md.tmpl."""
    c = design.colors
    t = design.typography
    lo = design.layout

    # Overview fallback
    overview = design.overview or (
        f"{project_name} 的视觉设计系统，定义品牌色彩、排版规范与组件样式，"
        f"确保 AI 编码代理在生成 UI 时保持一致的视觉语言。"
    )
    brand_personality = design.brand_personality or "专业、简洁、现代"

    # Color descriptions
    color_desc = (
        f"调色板以高对比度中性色为基础，辅以单一强调色，"
        f"确保 WCAG AA 对比度（正文 4.5:1）。"
    )
    elevation_desc = _ELEVATION_LABEL.get(design.elevation, design.elevation) or _ELEVATION_LABEL["tonal-layers"]
    shapes_desc = _SHAPES_LABEL.get(design.shapes, design.shapes) or _SHAPES_LABEL["rounded"]

    # Layout description
    layout_desc = (
        f"采用 **{lo.spacing_system}** 间距体系，"
        f"移动端优先（Mobile-first），最大内容宽度 1280px。"
    )
    breakpoints = (
        f"| 断点 | 宽度 |\n| --- | --- |\n"
        f"| Mobile | {lo.mobile_breakpoint} |\n"
        f"| Tablet | {lo.tablet_breakpoint} |\n"
        f"| Desktop | {lo.desktop_breakpoint} |"
    )

    # Do's and Don'ts
    dos = design.dos or (
        "使用 primary 色仅用于每屏最重要的单一操作",
        "保持 WCAG AA 对比度（正文 4.5:1，大文字 3:1）",
        "遵循 8px 间距网格，保持视觉节奏一致",
        "在同一视图中保持圆角风格统一",
    )
    donts = design.donts or (
        "不要在同一屏幕使用超过两种字重",
        "不要混用圆角与直角元素",
        "不要使用纯黑（#000000）作为文字色，优先使用深灰",
        "不要仅凭颜色传达信息（需配合图标或文字）",
    )

    return {
        # YAML front matter tokens
        "primary_color_hex": c.primary,
        "secondary_color_hex": c.secondary,
        "background_color_hex": c.background,
        "surface_color_hex": c.surface,
        "text_color_hex": c.text,
        "heading_font": t.heading_font,
        "body_font": t.body_font,
        # Markdown prose
        "design_overview": overview,
        "brand_personality": brand_personality,
        "visual_feeling": design.brand_personality or "专业、易用、值得信赖",
        "colors_description": color_desc,
        "primary_color_usage": "主品牌色，用于主要操作按钮、链接与关键高亮。",
        "secondary_color_usage": "辅助色，用于次要操作、边框与元数据文字。",
        "background_color_usage": "页面底色，提供柔和的视觉基底。",
        "surface_color_usage": "卡片与组件表面色，与背景形成微妙层次。",
        "text_color_usage": "主文字色，确保最高可读性。",        "color_semantics": (
            "- **交互色**：primary，用于所有可点击元素\n"
            "- **内容色**：text，用于正文与标题\n"
            "- **结构色**：secondary，用于分割线、占位符与辅助说明\n"
            "- **背景色**：background / surface，构建视觉层次"
        ),
        "typography_description": (
            f"排版策略以 **{t.heading_font}** 承载标题层级，"
            f"以 **{t.body_font}** 支撑正文可读性，"
            f"通过字重与字号差异建立清晰的信息层次。"
        ),
        "heading_font_usage": f"用于所有标题层级（H1–H3），传达品牌调性。",
        "body_font_usage": f"用于正文、标签与辅助说明，优先保证长文可读性。",
        "layout_description": layout_desc,
        "spacing_system": lo.spacing_system,
        "responsive_breakpoints": breakpoints,
        "elevation_description": elevation_desc,
        "shapes_description": shapes_desc,
        "button_guidelines": (
            "- **Primary Button**：`background: primary`，`color: surface`，`rounded: md`，`padding: 12px 24px`\n"
            "- **Secondary Button**：`background: transparent`，`border: 1px solid secondary`，`color: text`\n"
            "- **Disabled 状态**：opacity 0.4，禁止 pointer-events\n"
            "- **Hover 状态**：primary 色加深 10%（或 secondary 色加深 10%）"
        ),
        "card_guidelines": (
            "- `background: surface`，`rounded: lg`，`padding: 24px`\n"
            "- 使用色调分层而非阴影区分卡片与背景\n"
            "- 卡片间距遵循 spacing.lg（24px）"
        ),
        "input_guidelines": (
            "- `border: 1px solid secondary`，`rounded: sm`，`padding: 8px 12px`\n"
            "- Focus 状态：`border-color: primary`，`outline: 2px solid primary` (offset 2px)\n"
            "- Error 状态：`border-color: error`，配合错误提示文字\n"
            "- Label 位于输入框上方，使用 caption 字体规格"
        ),
        "other_components": (
            "- **Chips**：`rounded: full`，`padding: 4px 12px`，`background: surface`\n"
            "- **Tooltips**：`background: text`，`color: surface`，`rounded: sm`，`padding: 4px 8px`\n"
            "- **Dividers**：`border: 1px solid secondary`，opacity 0.2"
        ),
        "design_dos": _bullet_list(list(dos)),
        "design_donts": _bullet_list(list(donts)),
    }


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

    ctx: Dict[str, str] = {
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

    # Merge design system context (all keys needed by design.md.tmpl)
    ctx.update(_design_context(response.design, project.project_name))

    return ctx
