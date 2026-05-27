# Design Doc · VoiceCook

> 工程设计文档（Google 风格）：**约束实现方式**，记录关键决策、约束程度与备选方案。
> 产品需求见 [spec.md](spec.md)；落定后的架构参考见 [architecture.md](architecture.md)。

## Context & Scope

语音引导的免动手烹饪助手。

本设计覆盖支撑上述产品所需的技术方案；不覆盖产品需求本身（见 [spec.md](spec.md)）。

## Goals / Non-Goals（技术）

**Goals**

- 让用户做饭时无需触碰屏幕

**Non-Goals**

- _（列出本设计明确不解决的技术问题。）_

## 提议的设计

- **架构模式**：无服务器 (Serverless)
- **技术栈**：Python / FastAPI / SQLite
- _（展开核心数据流、关键组件与交互；具体落点见 [architecture.md](architecture.md)。）_

## Degree of Constraint（约束程度）

区分**硬约束**（实现者不得偏离）与**可裁量**（留给实现者判断）：

- 硬约束：架构模式（无服务器 (Serverless)）、数据库（SQLite）。
- 可裁量：模块内部实现、次要库选择、文件组织细节。

## Alternatives Considered（备选方案）

- _（列出考虑过但未采用的方案及未采用的理由——这是设计文档的核心价值所在。）_

## Cross-Cutting Concerns

### 安全 / 隐私

- _（鉴权与授权、数据最小化、在系统边界校验输入。）_

### 可观测性

- _（日志、指标、追踪：出问题时如何定位。）_

### 发布 / 回滚

- **云服务商**：未指定
- **容器化**：none
- **CI/CD**：未指定

## Open Questions

- _（尚未定论、需后续确认的点。）_

## 关联文档

- [Spec](spec.md)
- [Architecture](architecture.md)
- [Decisions](../../memory/decisions.md)
