# Harness Skill 测试计划（v1）

## 1) 规范校验

- 检查 `SKILL.md` frontmatter：
  - `name` 与目录名一致（`harness-skill`）
  - `description` 非空且包含触发语义
- 检查引用资源路径：
  - `references/interview-response.schema.json`
  - `references/runtime-compatibility.md`

## 2) 访谈流程测试

- Happy path：4 阶段完整跑通并进入确认页。
- Negative path：缺少必填（如项目名）时触发重问。
- Resume path：任一阶段中断后可恢复并继续。

## 3) 生成测试

- 首次生成：产出 `harness-map.md` 与 v1 文档子集。
- 二次生成：已有入口文件时执行区块级更新，不重复写入。
- 故障恢复：单文档失败时保留已生成文件并支持重试。

## 4) 跨平台一致性测试

对 Kiro / Cursor / Codex / Claude Code / OpenClaw / Hermes，输入同一测试用例，校验：

- 输出 JSON 顶层字段一致
- 架构枚举值一致（如 `architecturePattern`）
- `voiceEnabled` 条件分支行为一致

## 5) 性能目标

- 访谈响应：< 2s（平均）
- 单文档生成：< 5s（平均）
- 标准项目完整生成：< 60s
