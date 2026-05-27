---
name: harness-skill
description: |
  Conduct a four-phase project interview in chat and generate a cross-agent Harness Engineering documentation system.
  Use when the user wants harness docs, project interviews, architecture/requirements gathering, harness-map, AGENTS.md setup,
  or says 创建文档系统、生成 harness、项目访谈、Harness 文档、AI Agent 配置.
license: MIT
compatibility: Designed for Kiro, Cursor, Codex, Claude Code, OpenClaw, and Hermes. Requires file read/write in workspace root.
paths:
  - "specs/**"
  - "skills/**"
  - "**/*.md"
metadata:
  author: harness-team
  version: "0.3.0"
---

# Harness Skill

## When to Use

- User wants an **interview-style** workflow to define a project (not a one-shot doc dump).
- User wants Harness Engineering docs: `harness-map.md`, layered docs, agent entry files.
- User wants to **resume** an interrupted requirements interview.

## Primary Mode: Agent-Led Interview (默认)

**You (the agent) conduct the interview in this chat.** Ask questions; the user answers.  
Do **not** tell the user to run `interview.py` unless they explicitly ask for terminal/CLI mode.

### On activation

1. Read `references/agent-interview-protocol.md` and follow it step by step.
2. Check `.harness-skill-state.json` in the workspace root for resume.
3. Greet briefly, explain 4 phases, then ask **one logical question at a time**.
4. After each phase, write/update `.harness-skill-state.json` with collected `responses`.
5. After Phase 4, show a summary and wait for user confirmation before generating files.

### Interview phases

1. **Project Exploration** — name, description, goals, users, features  
2. **Agent Personality** — voice-enabled?, tone/style (if voice)  
3. **Architecture** — stack, pattern, deployment, integrations  
4. **Prototype Specs** — output format, fidelity, format-specific options  

Full question order, validation, and state transitions: `references/agent-interview-protocol.md`.

### Response shape

All collected data must match `references/interview-response.schema.json`.

## After Interview: Agent-Led Document Generation (默认)

**You (the agent) write the documents yourself, using your own judgment — not template fill-in.**
Read `references/agent-generation-protocol.md` and follow it. Core idea: reason about and
expand on the interview answers so each document is genuinely tailored to *this* project;
use AI for the writing wherever you can. Templates in `assets/templates/` are only a
structural skeleton and a minimum bar.

Only after the user confirms the summary:

1. Generate `harness-map.md` first, then the v1 layer docs (see `specs/harness-skill/tasks.md` §2),
   then the agent entry files — progressively, reporting progress per file.
2. Update entry files with **managed blocks only** (append/merge, never blind overwrite):
   `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/harness.mdc`. Markers:

```markdown
<!-- HARNESS:START -->
... harness-managed content ...
<!-- HARNESS:END -->
```

3. Keep writes inside the workspace root; confirm before overwriting existing whole-file docs;
   preserve already-written docs if one fails.
4. On success, remove `.harness-skill-state.json`. Suggest the user run the validator
   (`scripts/validate.py --output .`) and start at `harness-map.md`.

## Fallback: CLI scripts (optional, deterministic)

Use only when the user requests terminal/CI mode or the runtime cannot maintain chat state.
These are **rule-based** (template substitution) and produce less rich content than the
agent-led path above:

```bash
# Interview in the terminal
python3 skills/harness-skill/scripts/interview.py [--resume]

# Deterministic generation from a saved response JSON
python3 skills/harness-skill/scripts/generate.py --response harness-interview-response.json --root .

# Validate a generated tree (works regardless of how it was generated)
python3 skills/harness-skill/scripts/validate.py --output .
```

## References

| File | Purpose |
|------|---------|
| `references/agent-interview-protocol.md` | **Agent interview playbook (read first)** |
| `references/agent-generation-protocol.md` | **Agent generation playbook (read before writing docs)** |
| `references/interview-response.schema.json` | JSON contract for `responses` |
| `references/runtime-compatibility.md` | Cross-platform notes |
| `references/test-plan.md` | Validation checklist |
| `assets/templates/` | Structure skeletons (agent reference + fallback engine) |
| `assets/examples/` | Sample output (simple project + voice-enabled app) |
| `scripts/interview.py` | CLI interview — fallback only |
| `scripts/generate.py` | Deterministic generator — fallback/CI only |
| `scripts/validate.py` | Output + spec validator (dead links, residue, empty docs) |

## Rules

- CommonMark + relative links in generated docs.
- UTF-8 encoding.
- Idempotent entry-file updates (no duplicate HARNESS blocks).
- Never write outside workspace root without explicit consent.
