<!-- HARNESS:START -->
# Claude Code Instructions · TaskFlow

This project uses the Harness Engineering system. Start at [harness-map.md](harness-map.md).

TaskFlow's core bet: the shared board must be real-time and trustworthy enough to replace the
daily sync meeting. Most architecture decisions trace back to that.

## Key files

- Design (the "why"): [harness/platform/design.md](harness/platform/design.md)
- Architecture (real-time, optimistic locking, data model): [harness/platform/architecture.md](harness/platform/architecture.md)
- Decisions (with rationale): [memory/decisions.md](memory/decisions.md)

## Workflow

1. Before editing board/task-state code, read the architecture doc and `memory/decisions.md`.
2. Record any new trade-off (tech debt, scope cut, selection) in `memory/decisions.md` as a
   D-XXX entry, with its reason and cost.
3. Keep all generated docs in CommonMark with relative links.
<!-- HARNESS:END -->
