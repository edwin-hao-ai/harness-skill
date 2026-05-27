# Agent 访谈协议（Agent-Led Interview）

本文件定义 Agent 在激活 `harness-skill` 后应如何**在对话中**主持访谈。  
CLI 脚本 `scripts/interview.py` 仅作离线/自动化 fallback，**默认不使用**。

## 激活后第一件事

1. 检查项目根目录是否存在 `.harness-skill-state.json`。
2. 若存在且 `currentPhase` 未完成：
   - 向用户说明可「继续上次访谈」或「重新开始」。
   - 继续则读取 `responses` 与 `currentPhase`，从当前阶段/问题继续。
3. 若不存在或用户选择重新开始：
   - 初始化状态并写入文件（见下方 State 格式）。
   - 用简短介绍说明 4 个阶段与预计时长，然后开始 Phase 1。

## 访谈原则（必须遵守）

- **由 Agent 提问，用户回答**；不要要求用户自行运行 Python 脚本。
- **每次只推进一个逻辑步骤**（1–3 个相关问题），等用户回复后再继续。
- 使用用户语言（用户用中文则全程中文）。
- 必填项缺失时**同一步重问**，不要跳过。
- 每完成一个 Phase，立即更新 `.harness-skill-state.json`。
- Phase 4 结束后展示**分阶段总结**，询问确认；用户确认后再进入文档生成。
- 用户说「暂停/稍后继续」时保存状态并明确告知恢复方式。

## State 文件格式

路径：`.harness-skill-state.json`（项目根目录）

```json
{
  "version": "0.1.0",
  "currentPhase": "projectExploration",
  "currentStep": "projectName",
  "completedPhases": [],
  "responses": {}
}
```

`currentPhase` 取值：`projectExploration` | `agentPersonality` | `architecture` | `prototypeSpecs` | `summary` | `generating` | `completed`

`responses` 结构必须符合 `references/interview-response.schema.json`。

## Phase 1: Project Exploration

按顺序收集，写入 `responses.projectExploration`：

| Step | 提问要点 | 必填 |
|------|----------|------|
| projectName | 项目名称是什么？ | 是 |
| projectDescription | 用 1–3 句话描述项目 | 是 |
| projectGoals | 主要目标有哪些？（可多条） | 是 |
| successCriteria | 如何衡量成功？（可多条） | 建议 |
| targetUsers | 谁会使用？每种用户：名称、描述、主要用例 | 是，≥1 |
| coreFeatures | 核心功能：名称、描述、优先级 high/medium/low | 是，≥1 |

Phase 1 完成后：`completedPhases` 追加 `projectExploration`，`currentPhase` → `agentPersonality`。

## Phase 2: Agent Personality

写入 `responses.agentPersonality`：

1. 产品是否包含语音交互？（是/否）→ `voiceEnabled`
2. 若 `voiceEnabled === true`，继续问：
   - 语调：`professional` | `friendly` | `casual` | `formal`
   - 风格：`concise` | `detailed` | `technical` | `accessible`
   - 正式程度：1–10
3. 若否，仅保留 `{ "voiceEnabled": false }`，跳过语音细节。

完成后：`currentPhase` → `architecture`。

## Phase 3: Architecture

写入 `responses.architecture`：

1. 技术栈：语言、框架、数据库（各至少 1 项或明确「无」）
2. 架构模式：`monolith` | `microservices` | `serverless` | `hybrid`
3. 部署：云服务商、容器化（docker/kubernetes/none）、CI/CD 平台
4. 第三方集成（可选）：名称、类型 api/sdk/service、用途

完成后：`currentPhase` → `prototypeSpecs`。

## Phase 4: Prototype Specs

写入 `responses.prototypeSpecs`：

1. 输出格式：`html` | `markdown` | `wirescript`
2. 保真度：`low` | `medium` | `high`
3. 若 html → 问 CSS 框架；若 markdown → 问文档风格

完成后：`currentPhase` → `summary`。

## 总结与确认

向用户展示四段摘要（项目 / Agent 性格 / 架构 / 原型），并列出将生成的文档清单（至少 v1 子集）。

询问：

- **确认并生成** → `currentPhase` = `generating`，开始文档生成流程
- **返回修改** → 回到指定 Phase 重问对应字段
- **取消** → 保留 state，不删除

用户确认后：

1. 将最终 `responses` 写入 `harness-interview-response.json`（可选备份）
2. 执行文档生成（见 SKILL.md Workflow 第 4 步）
3. 成功后删除 `.harness-skill-state.json`，`currentPhase` → `completed`

## 示例开场（Agent 可直接使用）

> 我将通过 4 个阶段帮你梳理项目并生成 Harness 文档系统：项目探索 → Agent 性格 → 架构 → 原型规范。  
> 可以随时说「暂停」，我会保存进度到 `.harness-skill-state.json`。  
>  
> **第一个问题：你的项目名称是什么？**

## 示例单步提问（避免一次问太多）

❌ 不好：「请告诉我项目名、描述、目标、用户和功能。」  
✅ 好：「项目名称是什么？」→ 等回答 → 「用一两句话描述这个项目解决什么问题？」

## 与 Schema 对齐

生成或更新 `responses` 时，字段名与枚举值必须与 `interview-response.schema.json` 一致。  
不确定时读取该 schema 文件再写入 state。
