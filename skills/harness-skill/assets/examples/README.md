# 示例输出

两个示例展示 Harness Skill 的两条生成路径，可直接对照。

## `simple-project/` — agent 主路径（AI 撰写）

普通（非语音）项目 TaskFlow。文档由 **agent 亲自撰写**：在访谈素材之上做了推理与扩展
（实时同步约束、并发冲突处理、备选方案权衡等），代表 SKILL.md 的**默认/首选**生成方式。
注意它的 Platform 层是三分模型：

- `spec.md` — 产品需求（做什么、为谁、怎么算成功）
- `design.md` — Google 风格工程设计文档（约束程度、备选方案、横切关注点）
- `architecture.md` — 落定后的架构速查

## `voice-enabled-app/` — 兜底脚本（模板替换）

语音项目 VoiceCook，由 `scripts/generate.py` 确定性生成（模板替换）。用来展示：

- 条件生成：`voiceEnabled = true` → 多出 `harness/platform/voice.md`。
- 兜底路径的结构正确、可校验，但内容深度不如 agent 主路径——这正是我们默认用 AI 生成的原因。

## 复现

```bash
# 兜底脚本生成（如 voice 示例）
python3 skills/harness-skill/scripts/generate.py \
  --response tests/fixtures/voice-response.json \
  --root /tmp/voice-demo

# 校验任意生成树
python3 skills/harness-skill/scripts/validate.py --output /tmp/voice-demo
```
