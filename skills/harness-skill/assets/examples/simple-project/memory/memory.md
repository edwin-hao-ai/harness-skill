# Memory Index · TaskFlow

> 记忆系统入口。跨会话需要保留的上下文集中在 `memory/`。

## 索引

- [Decisions](decisions.md) — 关键架构/产品决策及其理由。

## 用法

- 任何会影响后续工作的取舍（技术选型、范围裁剪、已知技术债）都记进 [decisions.md](decisions.md)，
  写明**理由**，方便后人理解"当时为什么这样定"。
- TaskFlow 的几个决策彼此相关：单体、实时同步、乐观锁，都是为了同一个目标——"看板可信"。
  阅读时连起来看。
