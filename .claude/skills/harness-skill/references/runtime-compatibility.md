# Runtime Compatibility Notes

## Target Runtimes

- Kiro
- Cursor
- Codex
- Claude Code
- OpenClaw
- Hermes

## Compatibility Strategy

1. **Primary path**: Agent-led interview in chat (see `agent-interview-protocol.md`).
2. Keep skill instructions platform-neutral (no proprietary prompt syntax).
3. Keep output contract in JSON schema (`interview-response.schema.json`).
4. Keep generated docs in CommonMark with relative paths.
5. Keep entry file updates idempotent using managed blocks.
6. CLI `interview.py` is fallback only; do not require it for normal use.

## Cursor-Specific Notes

- Cursor discovers skills from:
  - `.cursor/skills/`
  - `.agents/skills/`
  - plus compatible directories including `.claude/skills/` and `.codex/skills/`
- Cursor supports optional frontmatter fields:
  - `paths`
  - `disable-model-invocation`

## Kiro-Specific Notes

- Kiro discovers skills from:
  - `.kiro/skills/`
  - `~/.kiro/skills/`

## Portability Checklist

- No hard dependency on a single runtime.
- No platform-only markdown extensions.
- No absolute paths in skill references.
