"""Immutable data model for a Harness interview response.

Mirrors ``references/interview-response.schema.json``. All structures are
frozen dataclasses so that, once parsed, a response cannot be mutated in
place — generation reads it but never changes it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


class ResponseError(ValueError):
    """Raised when an interview response is structurally invalid."""


def _require(mapping: Dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping or mapping[key] in (None, "", [], {}):
        raise ResponseError(f"缺少必填字段：{where}.{key}")
    return mapping[key]


def _as_str_tuple(value: Any, where: str) -> Tuple[str, ...]:
    if not isinstance(value, list):
        raise ResponseError(f"{where} 必须是字符串数组")
    return tuple(str(item) for item in value)


@dataclass(frozen=True)
class TargetUser:
    name: str
    description: str
    primary_use_cases: Tuple[str, ...]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TargetUser":
        return TargetUser(
            name=str(_require(data, "name", "targetUser")),
            description=str(_require(data, "description", "targetUser")),
            primary_use_cases=_as_str_tuple(
                _require(data, "primaryUseCases", "targetUser"),
                "targetUser.primaryUseCases",
            ),
        )


@dataclass(frozen=True)
class Feature:
    name: str
    description: str
    priority: str  # high | medium | low

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Feature":
        priority = str(data.get("priority", "medium")).lower()
        if priority not in {"high", "medium", "low"}:
            priority = "medium"
        return Feature(
            name=str(_require(data, "name", "feature")),
            description=str(_require(data, "description", "feature")),
            priority=priority,
        )


@dataclass(frozen=True)
class ProjectExploration:
    project_name: str
    project_description: str
    project_goals: Tuple[str, ...]
    success_criteria: Tuple[str, ...]
    target_users: Tuple[TargetUser, ...]
    core_features: Tuple[Feature, ...]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ProjectExploration":
        users = _require(data, "targetUsers", "projectExploration")
        features = _require(data, "coreFeatures", "projectExploration")
        return ProjectExploration(
            project_name=str(_require(data, "projectName", "projectExploration")),
            project_description=str(
                _require(data, "projectDescription", "projectExploration")
            ),
            project_goals=_as_str_tuple(
                _require(data, "projectGoals", "projectExploration"),
                "projectExploration.projectGoals",
            ),
            success_criteria=_as_str_tuple(
                data.get("successCriteria", []), "projectExploration.successCriteria"
            ),
            target_users=tuple(TargetUser.from_dict(u) for u in users),
            core_features=tuple(Feature.from_dict(f) for f in features),
        )


@dataclass(frozen=True)
class AgentPersonality:
    voice_enabled: bool
    tone: Optional[str] = None
    style: Optional[str] = None
    formality: Optional[int] = None

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> "AgentPersonality":
        if not data:
            return AgentPersonality(voice_enabled=False)
        formality = data.get("formality")
        return AgentPersonality(
            voice_enabled=bool(data.get("voiceEnabled", False)),
            tone=data.get("tone"),
            style=data.get("style"),
            formality=int(formality) if isinstance(formality, int) else None,
        )


@dataclass(frozen=True)
class TechStack:
    languages: Tuple[str, ...] = ()
    frameworks: Tuple[str, ...] = ()
    databases: Tuple[str, ...] = ()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TechStack":
        return TechStack(
            languages=_as_str_tuple(data.get("languages", []), "techStack.languages"),
            frameworks=_as_str_tuple(
                data.get("frameworks", []), "techStack.frameworks"
            ),
            databases=_as_str_tuple(data.get("databases", []), "techStack.databases"),
        )


@dataclass(frozen=True)
class Deployment:
    cloud_provider: Optional[str] = None
    containerization: Optional[str] = None
    cicd_platform: Optional[str] = None

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> "Deployment":
        if not data:
            return Deployment()
        return Deployment(
            cloud_provider=data.get("cloudProvider") or None,
            containerization=data.get("containerization") or None,
            cicd_platform=data.get("cicdPlatform") or None,
        )


@dataclass(frozen=True)
class Integration:
    name: str
    type: str  # api | sdk | service
    purpose: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Integration":
        return Integration(
            name=str(_require(data, "name", "integration")),
            type=str(data.get("type", "api")),
            purpose=str(_require(data, "purpose", "integration")),
        )


@dataclass(frozen=True)
class Architecture:
    tech_stack: TechStack
    architecture_pattern: str  # monolith | microservices | serverless | hybrid
    deployment: Deployment = field(default_factory=Deployment)
    integrations: Tuple[Integration, ...] = ()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Architecture":
        pattern = str(_require(data, "architecturePattern", "architecture")).lower()
        if pattern not in {"monolith", "microservices", "serverless", "hybrid"}:
            raise ResponseError(f"未知的 architecturePattern：{pattern}")
        integrations = data.get("integrations", []) or []
        return Architecture(
            tech_stack=TechStack.from_dict(
                _require(data, "techStack", "architecture")
            ),
            architecture_pattern=pattern,
            deployment=Deployment.from_dict(data.get("deployment")),
            integrations=tuple(Integration.from_dict(i) for i in integrations),
        )


@dataclass(frozen=True)
class PrototypeSpecs:
    output_format: str  # html | markdown | wirescript
    fidelity_level: str  # low | medium | high
    css_framework: Optional[str] = None
    doc_style: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PrototypeSpecs":
        fmt = str(_require(data, "outputFormat", "prototypeSpecs")).lower()
        if fmt not in {"html", "markdown", "wirescript"}:
            raise ResponseError(f"未知的 outputFormat：{fmt}")
        fidelity = str(_require(data, "fidelityLevel", "prototypeSpecs")).lower()
        if fidelity not in {"low", "medium", "high"}:
            raise ResponseError(f"未知的 fidelityLevel：{fidelity}")
        return PrototypeSpecs(
            output_format=fmt,
            fidelity_level=fidelity,
            css_framework=data.get("cssFramework") or None,
            doc_style=data.get("docStyle") or None,
        )


@dataclass(frozen=True)
class InterviewResponse:
    project: ProjectExploration
    personality: AgentPersonality
    architecture: Architecture
    prototype: PrototypeSpecs

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "InterviewResponse":
        if not isinstance(data, dict):
            raise ResponseError("响应必须是 JSON 对象")
        return InterviewResponse(
            project=ProjectExploration.from_dict(
                _require(data, "projectExploration", "response")
            ),
            personality=AgentPersonality.from_dict(data.get("agentPersonality")),
            architecture=Architecture.from_dict(
                _require(data, "architecture", "response")
            ),
            prototype=PrototypeSpecs.from_dict(
                _require(data, "prototypeSpecs", "response")
            ),
        )
