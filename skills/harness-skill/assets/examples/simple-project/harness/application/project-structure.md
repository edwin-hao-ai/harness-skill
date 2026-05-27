# Project Structure · TaskFlow

> 基于架构模式：单体应用（Monolith）。目标是"现在是单体，但按模块切分，日后可拆"。

## 目录结构

```text
taskflow/
├── packages/
│   ├── shared/              # 前后端共享的领域类型（Task, Status, version 等）
│   │   └── src/types.ts
│   ├── server/              # Express 单体后端
│   │   └── src/
│   │       ├── modules/     # 按领域切分（未来拆服务的接缝）
│   │       │   ├── tasks/   # 看板：实体、乐观锁更新、状态流转
│   │       │   ├── comments/
│   │       │   └── notifications/  # Slack 推送（走异步队列）
│   │       ├── realtime/    # WebSocket 网关：广播 task.moved / task.commented
│   │       ├── db/          # 迁移、连接池
│   │       └── http/        # 路由、中间件、错误处理
│   └── web/                 # React 前端
│       └── src/
│           ├── board/       # 看板视图、拖拽、乐观更新与回滚
│           ├── comments/
│           └── lib/         # WebSocket 客户端、API 封装
├── tests/                   # 单元 + 集成
├── docs/                    # 指向本 harness 文档
└── deploy/                  # Dockerfile + GitHub Actions
```

## 关键约定

- **领域逻辑只进 `modules/`**：HTTP/WebSocket 只做协议适配，便于日后把某个 module 切成独立服务。
- **共享类型走 `packages/shared`**：`Task` 的 `status`、`version` 等在前后端是同一份定义，避免契约漂移。
- **实时与持久解耦**：`realtime/` 订阅领域事件后广播，不在请求主链路里直接发 WebSocket。

## 技术栈对应

| 维度 | 选型 | 落点 |
| --- | --- | --- |
| 语言 | TypeScript | 全仓 |
| 前端 | React | `packages/web` |
| 后端 | Express | `packages/server/http` |
| 数据库 | PostgreSQL | `packages/server/db` |

## 关联文档

- [Architecture](../platform/architecture.md) — 模块边界与实时/并发设计的依据。
