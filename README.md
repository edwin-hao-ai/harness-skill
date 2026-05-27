# Harness Skill

一个**跨 Agent**的访谈式 Skill：在对话中通过四阶段访谈梳理项目，然后生成一套可导航、可恢复、
可被多种 AI Agent（Kiro、Cursor、Codex、Claude Code、OpenClaw、Hermes）消费的 **Harness Engineering**
文档系统。

> 两条路径都默认走 **agent + AI**：由 agent 在对话里提问、由 agent 用自己的判断撰写文档。
> 仓库里另带一套**确定性脚本**作为 CI/测试与无法维持对话状态时的兜底。

## 触发方式

- **自动**：说"创建文档系统 / 生成 harness / 项目访谈 / Harness 文档 / AI Agent 配置"等，
  靠 `description` 语义匹配触发。
- **手动**：`/harness-skill`。

激活后 agent 会：检查 `.harness-skill-state.json` 是否可恢复 → 简介四阶段 → 一次问一个逻辑问题 →
每阶段结束写状态 → Phase 4 后给总结 → **你确认后**才开始生成文档。

## 四阶段访谈

1. **Project Exploration** — 名称、描述、目标、用户、功能
2. **Agent Personality** — 是否语音产品、语调/风格
3. **Architecture** — 技术栈、架构模式、部署、集成
4. **Prototype Specs** — 输出格式、保真度、格式相关选项

中断随时说"暂停"，状态存到 `.harness-skill-state.json`，下次可恢复。
详见 [agent-interview-protocol.md](skills/harness-skill/references/agent-interview-protocol.md)。

## 生成的文档模型（v1 冻结集）

| 层 | 文档 | 职责 |
| --- | --- | --- |
| Index | `harness-map.md` | 中央导航索引 |
| Platform | `spec.md` | 产品需求：做什么、为谁、怎么算成功 |
| Platform | `design.md` | Google 风格工程设计文档：**约束实现**，记录决策/约束程度/备选方案 |
| Platform | `architecture.md` | 落定后的架构速查：栈、组件、数据模型、部署 |
| Platform | `voice.md` | 仅 `voiceEnabled=true` 时生成 |
| Domain | `use-cases.md` | 每个核心功能至少一个用例 |
| Application | `project-structure.md` | 反映架构模式的目录组织 |
| Interface | `user-guide.md` | 面向目标用户的说明 |
| Memory | `memory.md` / `decisions.md` | 记忆索引与决策记录 |
| Entry | `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/harness.mdc` | Agent 入口（managed block，幂等合并） |

入口文件用 `<!-- HARNESS:START/END -->` 区块**幂等合并**，绝不整文件覆盖用户内容。
生成约束与撰写心法见 [agent-generation-protocol.md](skills/harness-skill/references/agent-generation-protocol.md)。

## 兜底脚本（CI / 无对话状态时）

```bash
# 终端访谈
python3 skills/harness-skill/scripts/interview.py [--resume]

# 从访谈响应 JSON 确定性生成
python3 skills/harness-skill/scripts/generate.py --response harness-interview-response.json --root .

# 校验生成结果（死链 / 空文档 / 占位符残留 / SKILL 规范）
python3 skills/harness-skill/scripts/validate.py --output .
python3 skills/harness-skill/scripts/validate.py --skill skills/harness-skill
```

## 示例

- [`simple-project/`](skills/harness-skill/assets/examples/simple-project) — agent 主路径（AI 撰写）
- [`voice-enabled-app/`](skills/harness-skill/assets/examples/voice-enabled-app) — 兜底脚本（模板替换）

## 开发与测试

```bash
python3 -m pytest        # 单元 + 集成测试
```

跨 runtime 镜像（`.kiro/.cursor/.agents/.claude/.codex`）由脚本同步，**只改 `skills/harness-skill/`，
然后运行**：

```bash
bash skills/harness-skill/scripts/sync-runtime-skills.sh
```

规范与计划：[specs/harness-skill/](specs/harness-skill/)。
