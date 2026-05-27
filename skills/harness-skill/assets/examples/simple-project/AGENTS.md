<!-- HARNESS:START -->
# Agent Instructions · TaskFlow

This project uses the Harness Engineering documentation system. TaskFlow is a lightweight
task-board tool for small teams; its guiding bet is "make the board trustworthy enough to
replace the daily sync meeting." Keep that in mind when reasoning about changes.

Start with [harness-map.md](harness-map.md) for the full navigation index.

| Layer | Entry |
| --- | --- |
| Platform | [harness/platform/design.md](harness/platform/design.md) |
| Domain | [harness/domain/use-cases.md](harness/domain/use-cases.md) |
| Application | [harness/application/project-structure.md](harness/application/project-structure.md) |
| Interface | [harness/interface/user-guide.md](harness/interface/user-guide.md) |
| Memory | [memory/memory.md](memory/memory.md) |

Before changing anything that touches the board or task state, read
[harness/platform/architecture.md](harness/platform/architecture.md) (real-time + optimistic
locking) and [memory/decisions.md](memory/decisions.md) — several decisions there are
load-bearing for "board trustworthiness."
<!-- HARNESS:END -->
