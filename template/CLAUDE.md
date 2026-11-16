# <Project name>

<!-- Loaded on every call: keep under 5 KB. Fixed rules and pointers only, no status or history. Not committed to git. -->

<One paragraph: what this is, the language and stack, how it's run.>

## Commands

- Build: `<cmd>`
- Test: `<cmd>`
- Run: `<cmd>`

## Layout

| Path | What |
|---|---|
| `src/` | <...> |

## Docs (look things up, don't read whole)

| File | Use |
|---|---|
| `PROMPT.md` | Session brief. Read once when told "follow PROMPT.md". Part C is this session's one task. |
| `NEXT.md` | Open work queue (< 20 KB), with stable IDs. Read at session start. |
| `docs/README.md` | Index of subsystem docs. Read the doc for the area you're changing. |
| `PROGRESS.md` | Session log and history. Grep only. |
| `docs/BACKLOG.md` | Cold NEXT items, same IDs. Grep only. Move an item to NEXT before working on it. |
| `docs/LESSONS.md` | Full list of tooling and harness gotchas. Grep only. |

## Rules

- One task per session (PROMPT.md Part C). After the bookkeeping, report and stop.
- When you find a quirk or an architectural fact, write it into its subsystem doc (one home per fact).
- Searches across many files go to an Explore subagent. Single lookups stay direct.
- Wait for long jobs with `run_in_background` or Monitor, not `sleep` loops.
- Crop or downscale screenshots before reading them.
- <Project-specific: files never to edit, things that break the build, ...>
