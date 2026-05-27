# Project Structure · VoiceCook

> 基于架构模式：无服务器 (Serverless)。

## 目录结构

```text
project-root/
├── functions/     # 各函数入口
├── lib/           # 共享逻辑
├── events/        # 事件/触发器定义
└── infra/         # IaC 配置

```

## 技术栈对应

| 维度 | 选型 |
| --- | --- |
| 编程语言 | Python |
| 框架 | FastAPI |
| 数据库 | SQLite |

## 关联文档

- [Architecture](../platform/architecture.md)
