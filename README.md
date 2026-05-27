# Harness Skill

**English** · [中文](README.zh-CN.md)

A **cross-agent**, interview-style Skill: it runs a four-phase project interview in chat,
then generates a navigable, resumable **Harness Engineering** documentation system that
multiple AI agents (Kiro, Cursor, Codex, Claude Code, OpenClaw, Hermes) can consume.

> Both halves default to **agent + AI**: the agent asks the questions and the agent *writes*
> the docs using its own judgment. A deterministic script set ships alongside as a fallback
> for CI/testing and runtimes that can't hold chat state.

## How it triggers

- **Automatically** — say things like "create a doc system / generate harness / project
  interview / Harness docs / AI agent config" (matched against the skill `description`).
- **Manually** — `/harness-skill`.

Once active, the agent will: check `.harness-skill-state.json` for a resumable session →
introduce the four phases → ask **one logical question at a time** → persist state after
each phase → show a summary after Phase 4 → and only generate files **after you confirm**.

## The four-phase interview

1. **Project Exploration** — name, description, goals, users, features
2. **Agent Personality** — voice-enabled? tone/style (if voice)
3. **Architecture** — stack, pattern, deployment, integrations
4. **Prototype Specs** — output format, fidelity, format-specific options

Say "pause" anytime; progress is saved to `.harness-skill-state.json` and can be resumed.
See [agent-interview-protocol.md](skills/harness-skill/references/agent-interview-protocol.md).

## Generated document model (frozen v1 set)

| Layer | Document | Responsibility |
| --- | --- | --- |
| Index | `harness-map.md` | Central navigation index |
| Platform | `spec.md` | Product requirements: what / for whom / how success is measured |
| Platform | `design.md` | Google-style engineering design doc that **constrains implementation** (degree of constraint, alternatives considered, cross-cutting concerns) |
| Platform | `architecture.md` | Settled architecture reference: stack, components, data model, deployment |
| Platform | `voice.md` | Generated only when `voiceEnabled = true` |
| Domain | `use-cases.md` | At least one use case per core feature |
| Application | `project-structure.md` | Directory layout reflecting the architecture pattern |
| Interface | `user-guide.md` | Guidance aimed at the target users |
| Memory | `memory.md` / `decisions.md` | Memory index and decision log |
| Entry | `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/harness.mdc` | Agent entry points (idempotent managed blocks) |

Entry files are merged via `<!-- HARNESS:START/END -->` blocks — **never** a blind overwrite
of user content. Generation constraints and the authoring mindset live in
[agent-generation-protocol.md](skills/harness-skill/references/agent-generation-protocol.md).

> **`spec.md` vs `design.md` vs `architecture.md`** — keep them distinct: `spec.md` is the
> product requirement ("what & why"); `design.md` is the engineering design doc whose job is
> to *constrain* the build (alternatives considered, what's fixed vs. flexible);
> `architecture.md` is the scannable reference of what was settled.

## Fallback scripts (CI / no chat state)

These are **rule-based** (template substitution) and produce thinner content than the
agent-led path — use them only for terminal/CI mode or when the runtime can't hold state:

```bash
# Terminal interview
python3 skills/harness-skill/scripts/interview.py [--resume]

# Deterministic generation from a saved response JSON
python3 skills/harness-skill/scripts/generate.py --response harness-interview-response.json --root .

# Validate a generated tree (dead links / empty docs / unfilled placeholders / SKILL spec)
python3 skills/harness-skill/scripts/validate.py --output .
python3 skills/harness-skill/scripts/validate.py --skill skills/harness-skill
```

## Examples

- [`simple-project/`](skills/harness-skill/assets/examples/simple-project) — agent-authored (AI-written)
- [`voice-enabled-app/`](skills/harness-skill/assets/examples/voice-enabled-app) — fallback script (template substitution)

## Develop & test

```bash
python3 -m pytest        # unit + integration tests
```

Runtime mirrors (`.kiro/.cursor/.agents/.claude/.codex`) are kept in sync by a script —
**only edit `skills/harness-skill/`, then run**:

```bash
bash skills/harness-skill/scripts/sync-runtime-skills.sh
```

Spec and plan: [specs/harness-skill/](specs/harness-skill/).

## License

[MIT](LICENSE).
