# Harness Map · TaskFlow

> Harness Engineering 文档系统的中央导航索引。

TaskFlow 是一个面向小团队的轻量级任务协作工具，核心赌注是"用一块共享看板取代每日同步会"。
本系统的文档据此组织：上层文档定义"为什么这样做"，下层定义"怎么做"，记忆层保存"为什么当时这样决定"。

## Platform Layer

- [Spec](harness/platform/spec.md) — 产品需求：问题、目标/非目标、用户、功能、成功标准。
- [Design Doc](harness/platform/design.md) — Google 风格工程设计文档：约束程度、备选方案、横切关注点。
- [Architecture](harness/platform/architecture.md) — 落定后的架构速查：栈、实时通道、并发控制、数据模型。

## Domain Layer

- [Use Cases](harness/domain/use-cases.md) — 看板与评论两条核心流程的逐步用例与边界场景。

## Application Layer

- [Project Structure](harness/application/project-structure.md) — TypeScript 单体的目录组织与分层约定。

## Interface Layer

- [User Guide](harness/interface/user-guide.md) — 面向团队负责人的上手说明。

## Memory Layer

- [Memory Index](memory/memory.md) — 记忆系统入口。
- [Decisions](memory/decisions.md) — 关键架构/产品决策及其理由。

## Agent Entry Points

- [AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md) · [.cursor/rules/harness.mdc](.cursor/rules/harness.mdc)

---

_本示例由 agent 主路径撰写（非模板替换），用以展示 AI 生成的内容深度。_
