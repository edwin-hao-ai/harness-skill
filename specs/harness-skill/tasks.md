# Harness Skill v1 实施清单（可执行版）

## 0. 目标与范围

### v1 目标
- 提供平台无关的访谈式 Harness 能力，在 Kiro、Cursor、Codex、Claude Code、OpenClaw、Hermes 等主流 Agent 环境中都可发起 4 阶段访谈，并生成一套可导航、可恢复、可跨 Agent 消费的基础 Harness 文档系统。

### v1 必做（MVP）
- 访谈流程可完整跑通（含中断恢复）。
- 访谈引擎与平台适配层解耦（Interview Core + Platform Adapters）。
- 支持在 Kiro / Cursor / Codex / Claude Code / OpenClaw / Hermes 发起同构访谈流程（问题语义与输出一致）。
- 生成 `harness-map.md` 与 4 层核心文档（精简子集）。
- 自动检测并增量写入入口文件（`AGENTS.md`、`CLAUDE.md`），存在则 append/merge，不存在则创建。
- 支持 Cursor 规则文件生成与增量更新（`.cursor/rules/harness.mdc`）。
- 支持安全写入（路径校验、覆盖确认、失败保留已生成内容）。

### v1 暂缓（v1.1+）
- `.windsurf/rules/` 的完整定制化规则生成。
- 全量 27+ 文档一次性覆盖。
- 模板高级自定义 UI。
- 多平台兼容性自动回归套件。

---

## 实施状态（截至本次）

主路径确定为 **agent + AI 生成**；确定性脚本为兜底/测试。

**已交付**
- 访谈核心（CLI `interview.py` + agent 协议）、状态持久化、恢复分支。
- agent 生成协议 `references/agent-generation-protocol.md`（主路径）。
- Platform 三分文档模型：`spec.md`（需求）/ `design.md`（Google 风格设计文档，约束实现）/ `architecture.md`（架构速查）。
- 兜底确定性生成器 `scripts/generate.py` + `harness_gen/`（模板渲染、默认值回退、路径安全、
  managed-block 幂等合并、渐进式生成、条件 voice.md）。
- 13 个模板（`assets/templates/`）；2 个示例（agent 撰写 `simple-project` / 脚本生成 `voice-enabled-app`）。
- 校验脚本 `scripts/validate.py`（frontmatter / 死链 / 空文档 / 占位符残留）。
- 34 个 pytest 通过；6 个 runtime 镜像由 `sync-runtime-skills.sh` 同步，镜像内脚本独立可跑。
- README（根 + 示例）。

**仍待办（v1.1）**
- 跨 6 平台**自动**一致性回归矩阵（当前靠镜像同源 + 单源逻辑保证，未做自动 E2E 矩阵）。
- 性能基准量化（NFR：访谈<2s / 单文档<5s / 全量<60s 未实测）。
- `harness-map.md` 的"每层后增量回写"（当前为开头一次性写出完整索引，已满足"始终可用"）。

---

## 1. 里程碑规划

## M1：访谈核心引擎与状态机

### 任务
- [ ] 建立平台无关的 Interview Core（问题流、状态机、校验器、状态持久化接口）。
- [ ] 建立 Kiro 入口（`SKILL.md`，符合 Kiro/Agent Skills 规范，frontmatter 完整）。
- [ ] 建立 Cursor / Codex / Claude Code / OpenClaw / Hermes 适配入口（至少 MVP 级触发与恢复）。
- [ ] 实现 Interview Orchestrator（4 阶段状态机 + 中断/恢复入口）。
- [ ] 实现 Response Collector 基础数据结构与字段校验。
- [ ] 实现 `.harness-skill-state.json` 的保存、读取、清理逻辑。
- [ ] 实现“继续上次访谈 / 重新开始”分支。

### 验收标准（DoD）
- [ ] 从 Phase 1 可以连续推进到 Phase 4，状态正确流转。
- [ ] 任意阶段中断后可恢复到原问题上下文。
- [ ] 无效输入会被拦截并重试（至少覆盖：项目名为空、必填未答）。
- [ ] 在 Kiro / Cursor / Codex / Claude Code / OpenClaw / Hermes 中均可启动访谈并完成至少一次端到端流程。
- [ ] 同一输入在不同平台输出的结构化响应一致（字段级一致，允许文案细微差异）。
- [ ] 成功完成一次访谈后，状态文件可被删除。

### 交付物
- `SKILL.md`（Kiro）
- 平台适配层（Cursor / Codex / Claude Code / OpenClaw / Hermes）
- 访谈状态管理模块（Orchestrator / Collector / State）

---

## M2：模板系统与文档生成主链路

### 任务
- [ ] 搭建 Document Generator 主流程（TemplateEngine / Renderer / PathResolver）。
- [ ] 定义 v1 模板集合（最小可用文档子集）：
  - `harness-map.md`
  - `harness/platform/design.md`
  - `harness/platform/architecture.md`
  - `harness/domain/use-cases.md`
  - `harness/application/project-structure.md`
  - `harness/interface/user-guide.md`
  - `memory/memory.md`
  - `memory/decisions.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.cursor/rules/harness.mdc`
- [ ] 实现占位符渲染与默认值回退（可选问题可用默认值）。
- [ ] 实现条件生成样例（`voice.md` 按 `voiceEnabled` 控制，可先模板占位）。
- [ ] 实现入口文件注入策略：自动检测已有 `AGENTS.md` / `CLAUDE.md` 并 append/merge（非整体覆盖）。

### 验收标准（DoD）
- [ ] 一次访谈完成后可生成上述全部 v1 文档。
- [ ] 每份文档不包含未替换占位符（如 `{{...}}`）。
- [ ] 失败时保留已成功生成文档，且可重试失败文档。
- [ ] 所有内部链接均为相对路径，且引用有效。
- [ ] 已存在 `AGENTS.md` / `CLAUDE.md` 时，Harness 区块可幂等更新（重复执行不产生重复段落）。

### 交付物
- 文档生成模块
- v1 模板目录（assets/templates）

---

## M3：渐进式生成、索引更新与写入安全

### 任务
- [ ] 按顺序生成：`harness-map.md` -> 各层文档 -> Agent 入口。
- [ ] 每完成一个层级后增量更新 `harness-map.md`。
- [ ] 实现 `.cursor/rules/harness.mdc` 的创建或增量更新（存在则合并 Harness 规则段）。
- [ ] 增加路径安全校验（禁止写入项目根目录外）。
- [ ] 增加覆盖确认策略（检测已存在文件时提示）。
- [ ] 增加写权限与磁盘异常处理提示。

### 验收标准（DoD）
- [ ] 生成顺序符合规范，过程中可看到进度反馈。
- [ ] `harness-map.md` 始终可作为可用导航入口（即使生成中途失败）。
- [ ] 未经确认不覆盖已有文件。
- [ ] 对已有入口文件与 Cursor 规则文件执行“区块级更新”，不破坏用户自定义内容。
- [ ] 权限不足、路径非法、磁盘异常可返回可执行修复建议。

### 交付物
- 生成调度器（Generation Orchestrator）
- 写入安全与错误处理模块

---

## M4：质量门禁与发布准备

### 任务
- [ ] 补齐单元测试（状态流转、占位符替换、路径校验、条件生成）。
- [ ] 补齐集成测试（完整访谈 -> 文档生成 -> 索引验证）。
- [ ] 补齐跨平台一致性测试（同输入在各 Agent 平台的输出结构一致性）。
- [ ] 增加基础校验脚本（链接存在性、空文档检测、占位符残留检测）。
- [ ] 提供示例输出（至少 2 个：普通项目 / 语音项目）。
- [ ] 完成 README/使用说明（触发方式、恢复机制、常见错误）。

### 验收标准（DoD）
- [ ] 核心测试通过率 100%（本地基线）。
- [ ] 标准项目完整生成时间 < 60 秒（目标机）。
- [ ] 文档编码 UTF-8，跨平台换行处理正确。
- [ ] 新用户可在 10 分钟内跑通首次生成。
- [ ] 主流平台（Kiro / Cursor / Codex / Claude Code / OpenClaw / Hermes）均有通过记录。

### 交付物
- 测试与校验脚本
- 示例工程与使用文档

---

## 2. v1 文档范围（冻结版）

### Platform（3）
- [x] `harness/platform/spec.md`（产品需求：做什么/为谁/成功标准）
- [x] `harness/platform/design.md`（Google 风格工程设计文档：约束实现）
- [x] `harness/platform/architecture.md`（落定后架构速查）
- [x] `harness/platform/voice.md`（条件生成：voiceEnabled=true）

### Domain（1）
- [x] `harness/domain/use-cases.md`

### Application（1）
- [x] `harness/application/project-structure.md`

### Interface（1）
- [x] `harness/interface/user-guide.md`

### Memory（2）
- [x] `memory/memory.md`
- [x] `memory/decisions.md`

### Entry（3）
- [x] `AGENTS.md`
- [x] `CLAUDE.md`
- [x] `.cursor/rules/harness.mdc`

### Index（1）
- [x] `harness-map.md`

---

## 3. 关键技术决策（当前建议）

- 文档生成策略：模板驱动 + 分层调度（先索引后内容）。
- 写入策略：默认“新建优先”，覆盖必须显式确认。
- 入口文件策略：检测已有文件后进行区块级 append/merge，避免整文件覆盖。
- 状态恢复策略：阶段粒度持久化，恢复后回到未完成问题。
- 渲染策略：CommonMark 基线，禁止平台私有语法。
- 平台策略：访谈核心逻辑单一实现，平台仅做 I/O 适配，避免多套流程分叉。
- 可扩展策略：模板与生成器解耦，为 v1.1 扩展全量文档留接口。

---

## 4. 风险与缓解

- **风险：范围膨胀导致延期**
  - 缓解：严格按 v1 冻结文档清单交付，扩展项进入 v1.1。
- **风险：已存在项目文件冲突**
  - 缓解：预检 + 区块级 append/merge + 覆盖确认 + 失败回滚（至少保证不破坏已有内容）。
- **风险：访谈答案质量不稳定**
  - 缓解：关键字段校验 + 默认值 + 总结确认页可回改。
- **风险：跨 Agent 兼容性不一致**
  - 缓解：统一访谈核心引擎 + 适配层契约测试 + CommonMark 与相对路径规范。

---

## 5. 建议执行顺序（两周节奏）

### Week 1
- [ ] 完成 M1（核心引擎 + 多平台适配 + 恢复）
- [ ] 完成 M2（最小模板 + 主链路）

### Week 2
- [ ] 完成 M3（渐进式 + 安全）
- [ ] 完成 M4（测试 + 文档 + 示例）

---

## 6. 完成定义（项目级）

- [ ] 新项目可从 0 到 1 完成访谈并生成 v1 文档系统。
- [ ] Kiro / Cursor / Codex / Claude Code / OpenClaw / Hermes 均可发起访谈并得到一致结构输出。
- [ ] 访谈中断后可恢复且不丢数据。
- [ ] 文档索引、路径、引用可用，无占位符残留。
- [ ] 入口文件可指导 Agent 正确找到并使用 Harness 文档。
- [ ] 关键错误具备可恢复提示，不阻塞后续使用。

---

## 7. Skill 标准合规清单（基于 Agent Skills / Kiro / Cursor）

### 7.1 目录与发现路径
- [ ] Skill 主目录包含 `SKILL.md`（必需）。
- [ ] 可选目录按需提供：`scripts/`、`references/`、`assets/`。
- [ ] Kiro 发现路径兼容：`.kiro/skills/`（项目）、`~/.kiro/skills/`（全局）。
- [ ] Cursor 发现路径兼容：`.cursor/skills/`、`.agents/skills/`（项目），`~/.cursor/skills/`、`~/.agents/skills/`（全局）。
- [ ] 兼容 Cursor 对 `.claude/skills/`、`.codex/skills/` 的发现能力（用于跨生态落地）。

### 7.2 `SKILL.md` frontmatter 约束
- [ ] `name` 必填：1-64 字符，小写字母/数字/短横线，且与父目录同名。
- [ ] `description` 必填：1-1024 字符，明确“做什么 + 何时使用（Use when）”。
- [ ] 可选字段：`license`、`compatibility`、`metadata`、`allowed-tools`（实验）。
- [ ] Cursor 扩展字段：`paths`（文件范围）、`disable-model-invocation`（仅手动触发）。

### 7.3 内容与可移植性
- [ ] `SKILL.md` 主体使用 Markdown，避免平台私有语法。
- [ ] 主体控制在可读范围（建议 < 500 行），细节移到 `references/`。
- [ ] 资源引用使用相对路径，避免深层级链式引用。
- [ ] 指令描述采用“可执行步骤 + 输入输出示例 + 异常分支”结构。

---

## 8. 测试方案（最终 Skill 验收）

## T1：规范静态校验
- [ ] 校验 `SKILL.md` frontmatter 字段完整性与约束（name/description 格式、长度、目录同名）。
- [ ] 校验目录结构（必需/可选目录）。
- [ ] 校验引用路径有效性（`SKILL.md` -> `scripts/`/`references/`/`assets/`）。

**通过标准**
- [ ] 规范校验脚本返回成功。
- [ ] 无无效字段、无死链接、无非法命名。

## T2：访谈流程功能测试（平台无关核心）
- [ ] 四阶段访谈 Happy Path。
- [ ] 必填缺失、无效输入重试。
- [ ] 中断恢复（每一阶段都至少测一次）。
- [ ] 总结页回改与重新生成。

**通过标准**
- [ ] 结构化响应完整且字段一致。
- [ ] 状态文件 round-trip 一致（保存/恢复不丢字段）。

## T3：文档生成与幂等测试
- [ ] 首次生成（空仓库）成功。
- [ ] 二次生成（已有文档）执行区块级 append/merge。
- [ ] `AGENTS.md`、`CLAUDE.md`、`.cursor/rules/harness.mdc` 不重复注入。
- [ ] 失败中断后可重试，不破坏已有内容。

**通过标准**
- [ ] 重复执行不产生重复段落。
- [ ] 已有自定义内容保持不变。

## T4：跨平台适配测试矩阵
- [ ] Kiro：自动触发 + 手动触发（slash）。
- [ ] Cursor：自动触发 + `/skill-name` 手动触发 + `paths`/`disable-model-invocation` 行为验证。
- [ ] Codex：技能可发现并可执行访谈流程。
- [ ] Claude Code：技能可发现并可执行访谈流程。
- [ ] OpenClaw：技能可发现并可执行访谈流程。
- [ ] Hermes：技能可发现并可执行访谈流程。

**通过标准**
- [ ] 六平台均至少完成一次 E2E 访谈到文档生成。
- [ ] 同输入下输出 JSON 字段一致（允许提示文案差异）。

## T5：性能与稳定性测试
- [ ] 访谈响应 < 2 秒（平均）。
- [ ] 单文档生成 < 5 秒（平均）。
- [ ] 标准项目全量 v1 生成 < 60 秒。
- [ ] 连续 20 次回归执行无状态污染。

---

## 9. Cursor 中支持 Skill 的落地要点

- [ ] 将 Harness Skill 放在 `.cursor/skills/harness-skill/SKILL.md`（或 `.agents/skills/...`）。
- [ ] 若仓库已存在 `.claude/skills/` 或 `.codex/skills/`，保持同源内容，减少多份维护。
- [ ] 在 Cursor 中验证两类触发：
  - 自动触发：依赖 `description` 语义匹配；
  - 手动触发：`/harness-skill`。
- [ ] 若仅希望手动触发，设置 `disable-model-invocation: true`。
- [ ] 若仅对部分文件生效，设置 `paths`（如 `**/*.md`、`.kiro/specs/**`）。
