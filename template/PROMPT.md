# Session brief

<!-- Read once per session. Target < 10 KB (35 KB hard max). Parts A and B change rarely. Part C is replaced each
session. History goes to PROGRESS.md, never here. -->

Last updated: <date>, session <n>.

## Part A: the project and its current state

**Goal:** <what finished looks like>

**Architecture:** <5–10 lines. Link to `docs/<subsystem>.md` for details instead of copying them here.>

**Current state:**
- <what works>
- <what doesn't yet>
- <the main open question>

## Part B: method

- **Before changing anything:** grep `NEXT.md`, `PROGRESS.md` and `docs/` for the names the task touches
  (functions, files, IDs), then read the subsystem doc for that area. Don't read tier-4 files whole.
- **Verify before committing:** `<test command>`. <Any other check: lint, regression run, ...>
- **Harness rules** (the gotchas that come up every session; keep about 10 here, the full list is in `docs/LESSONS.md`):
  1. <...>

## Part C: this session's task

**One task.** Setup, then the task, then the bookkeeping below, then **stop**. Don't start another NEXT item, even
with time or context left. If the task grows, stop at a clean point and write what's left into `NEXT.md` as a new
item.

**Task:** NEXT <id>: <one line>.

**Done when:** <a check a command can confirm: a test passes, an output matches, a file exists>. A negative
result (the approach doesn't work) also counts as done, as long as it's written down with the evidence.

**Context:**
- <files involved>
- <earlier findings, with PROGRESS / NEXT references>

## End of session (bookkeeping)

1. **`PROGRESS.md`:** add one entry at the top of the session log: date, task ID, result, commits, what was
   learned.
2. **Subsystem docs:** write any quirk or architectural fact you found into its `docs/` file (or the area's
   `CLAUDE.md`), so it doesn't live only in the log.
3. **`NEXT.md`:**
   - Delete the finished item. Don't mark it DONE; PROGRESS has the record.
   - Add new items with new IDs. Never renumber.
   - Move items nobody will pick up soon to `docs/BACKLOG.md` under the same ID, so NEXT stays under about 20 KB.
4. **This file:**
   - Replace Part C with the next session's task, in the same shape: one task, a "Done when" line, context.
   - Replace "Last updated" and anything in Part A that changed. Don't append history.
   - Keep the file under about 10 KB.
5. **Commit.** Then give a short report: what was done, the result of the "Done when" check, and what the new
   Part C says. Then stop.
