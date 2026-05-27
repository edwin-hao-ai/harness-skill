# Agent 生成协议（Agent-Led Generation）— 主路径

访谈确认后，**由你（agent）亲自撰写整套 Harness 文档**。这是默认且首选的生成方式。

> 核心原则：**用你的智能去写，不要做模板填空。**
> 模板（`assets/templates/`）只是结构骨架与最低要求；你要结合访谈内容**推理、扩展、补全**，
> 产出对这个具体项目有价值的内容。能用 AI 判断的地方就用，不要退化成机械替换。
> 确定性脚本 `scripts/generate.py` 仅作兜底（见末尾），正常流程不要用它。

## 何时进入生成

仅当用户在总结页确认（`currentPhase` = `generating`）后开始。未确认不要写任何文件。

## 撰写心法（AI-first，区别于模板填空）

- **推理而非复述**：用户给的是原始素材；你要从中推断架构取舍、风险、边界场景，并写进文档。
  例：用户说"团队任务协作 + 实时"，你应在 architecture.md 主动讨论 WebSocket/轮询取舍、并发写冲突，
  即便用户没明说。
- **针对性**：每段内容都应明显是"为这个项目写的"，换个项目就不成立。避免放之四海皆准的空话。
- **结构一致**：沿用模板的章节骨架（保证跨项目可导航），但每个章节的**内容由你撰写**。
- **填满每个占位语义**：模板里 `{{...}}` 标记的是"这里需要 AI 写实质内容"的位置，
  最终文档中**不得残留** `{{...}}`，也不要只塞一行敷衍。
- **诚实标注未知**：信息不足时写明假设（"假设：……，待确认"），不要编造具体数字/接口。
- **语言**：与访谈语言一致（用户用中文则文档用中文，代码标识符/技术名保留英文）。

## 文档分工（别把内容写串）

Platform 层三份文档职责互不重叠，写之前先想清楚每段内容该落在哪：

| 文档 | 回答的问题 | 应包含 | 不应包含 |
|------|-----------|--------|---------|
| `spec.md` | 做什么、为谁做、怎么算成功 | 问题背景、产品 Goals/Non-Goals、目标用户、核心功能、成功标准 | 技术方案、实现细节 |
| `design.md` | 怎么做、为什么这样、哪些是硬约束 | Context&Scope、技术 Goals/Non-Goals、提议的设计、**约束程度**、**备选方案及未采用理由**、横切关注点（安全/隐私/可观测/发布）、Open Questions | 产品愿景（放 spec.md）、逐行实现 |
| `architecture.md` | 最终长什么样 | 技术栈、组件/模块图、数据模型、部署、集成（可读速查） | "为什么"的长篇论证（指回 design.md） |

> design.md 是 Google 风格的设计文档，**作用是约束实现**：备选方案与约束程度是它的核心价值，
> 不要退化成"架构总览"。产品需求一律进 spec.md。

## 生成顺序（渐进式，符合 requirements.md Req 15）

每写完一份就告诉用户进度（`✓ 路径`）。先写索引，最后写入口文件：

1. `harness-map.md` —— **先写**，即使后续中断它也是可用导航入口
2. Platform：`harness/platform/spec.md` → `design.md` → `architecture.md`（顺序即"需求→设计→落定"）
   - 仅当 `agentPersonality.voiceEnabled === true` 时追加 `harness/platform/voice.md`
3. Domain：`harness/domain/use-cases.md`（**每个 coreFeature 至少一个用例**，Req 10）
4. Application：`harness/application/project-structure.md`（结构须反映 `architecturePattern`，Req 11）
5. Interface：`harness/interface/user-guide.md`（须引用 `targetUsers`，Req 12）
6. Memory：`memory/memory.md`、`memory/decisions.md`
7. Agent 入口（managed block，见下）：`AGENTS.md`、`CLAUDE.md`、`.cursor/rules/harness.mdc`

v1 冻结清单见 `specs/harness-skill/tasks.md` §2；不要擅自扩展到全量 27 文档（那是 v1.1+）。

## 入口文件：managed block（必须幂等）

`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/harness.mdc` 可能已有用户内容。**绝不整文件覆盖**，
只维护一对标记之间的内容：

```markdown
<!-- HARNESS:START -->
... harness 托管内容 ...
<!-- HARNESS:END -->
```

- 文件不存在 → 新建（`.mdc` 先写 frontmatter，再写 block）。
- 已有 `HARNESS:START/END` → **只替换标记之间**，保留其余所有内容。
- 已存在但无标记 → 在文件末尾**追加** block，原内容一字不动。
- 重复生成必须 byte 级幂等：不得出现两个 HARNESS block。

## 写入安全（符合 Constraints / Req 19）

- **路径校验**：只写项目根目录内的相对路径；拒绝 `..` 越界与绝对路径。
- **覆盖确认**：整文件型 harness 文档（非入口文件）若已存在，先问用户是否覆盖；用户没同意就跳过并报告。
- **失败保留**：某份写失败时，保留已写成功的文件，报告失败项并允许重试，不要回滚或删除。
- **编码/格式**：UTF-8；CommonMark；内部链接用相对路径；代码块带语言标识。

## 收尾

1. 列出本次新建/更新/跳过/失败清单。
2. 成功后删除 `.harness-skill-state.json`，`currentPhase` → `completed`。
3. 建议用户先看 `harness-map.md`，并可运行校验：
   `python3 skills/harness-skill/scripts/validate.py --output .`

## 链接相对路径速查（从生成文件指向目标）

| 从 | 到 harness-map.md | 到同层文档 |
|----|------------------|-----------|
| `harness-map.md`（根） | — | `harness/platform/design.md` |
| `harness/platform/*.md` | `../../harness-map.md` | 同目录直接文件名 |
| `harness/domain/*.md` | `../../harness-map.md` | `../platform/design.md` |
| `memory/*.md` | `../harness-map.md` | 同目录直接文件名 |
| `.cursor/rules/harness.mdc` | `../../harness-map.md` | `../../harness/...` |

## 兜底：确定性脚本（默认不用）

仅当 runtime 无法维持对话状态、或用户明确要求 CI/批量复现时使用。它做的是**模板替换**，
内容不如你亲自撰写丰富：

```bash
python3 skills/harness-skill/scripts/generate.py --response harness-interview-response.json --root .
```

用它之后，仍建议你通读生成结果并按"撰写心法"补强关键章节。
