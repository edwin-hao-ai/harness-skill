# Architecture · TaskFlow

## 架构模式：单体应用（Monolith）

选单体是**主动决策，不是默认**。理由：

- 团队小、领域单一（看板 + 评论 + 通知），微服务的拆分收益此刻为负——只会换来跨服务事务与
  部署复杂度。
- 看板要求"任务移动后所有人即时看到"，**强一致的单库 + 单进程**最容易做到；跨服务最终一致
  会把"看板可信"这一核心卖点置于风险中。
- 留好出口：把领域逻辑收敛在 `modules/`（见 [Project Structure](../application/project-structure.md)），
  日后若通知或实时层需要独立伸缩，可按模块切出，而不必重写。

## 技术栈

| 维度 | 选型 | 备注 |
| --- | --- | --- |
| 语言 | TypeScript | 前后端同语言，看板的领域类型（Task/Status）可在前后端共享，减少契约漂移。 |
| 前端 | React | 看板是重交互 UI，组件化 + 乐观更新是拖拽体验的基础。 |
| 后端 | Express | 轻量，够用；REST 负责增删改查，实时另走通道（见下）。 |
| 数据库 | PostgreSQL | 需要事务保证"移动任务"原子可见；后续审计/筛选也吃关系型的红利。 |

## 实时同步（由 Design 的"砍掉会议"目标倒逼出的关键设计）

REST 不足以支撑"别人移动任务我立刻看到"。建议：

- **WebSocket 推送**任务变更事件（`task.moved` / `task.commented`），客户端订阅自己所在看板。
- 前端**乐观更新**：拖拽即时反映在本地，服务端确认后对账，失败则回滚并提示。
- MVP 阶段若不想立刻上 WebSocket，可用**短轮询（3–5s）兜底**，但需在 [decisions](../../memory/decisions.md)
  里记为已知技术债，因为它直接削弱"实时可信"。

## 并发写冲突

两人几乎同时移动同一任务是常态，必须正面处理：

- 任务行带 `version`（乐观锁）。更新携带读到的 version，服务端 `WHERE version = ?` 命中才写入并自增。
- 未命中 → 返回 409，前端拉取最新状态并提示"该任务刚被他人更新"。
- 这样避免"后写覆盖先写"导致看板与现实不符——同样是为"看板可信"服务。

## 数据模型草图

```text
Team (id, name)
User (id, team_id, name, role: lead|member)
Task (id, team_id, title, status: todo|doing|done, assignee_id, priority, version, updated_at)
Comment (id, task_id, author_id, body, created_at)
```

## 第三方集成

| 名称 | 类型 | 用途 | 设计要点 |
| --- | --- | --- | --- |
| Slack | api | 任务通知 | 任务被分配 / 状态变更 / 被 @ 时推送到 Slack，把"用户不在看板时"的触达补齐——这是异步替代会议的另一半。 |

> 建议：通知走**异步队列**（即便单体内进程内队列），避免 Slack 抖动拖慢看板主请求。

## 部署

- **云服务商**：AWS
- **容器化**：Docker（单镜像即可，符合单体定位）
- **CI/CD**：GitHub Actions（push → 测试 → 构建镜像 → 部署）

## 原型与界面

- 输出格式：HTML（可交互原型，贴合看板的拖拽特性）
- 保真度：medium
- CSS 框架：Tailwind

## 关联文档

- [Design](design.md) — 这些约束的来源。
- [Project Structure](../application/project-structure.md) — 上述模块边界如何落到目录。
