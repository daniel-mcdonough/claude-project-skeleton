# Setting up a project for Claude Code sessions

Instructions for a Claude Code session. To use them, tell a new session "Set up this project using
`<path to this repo>/NEW_PROJECT.md`". Below, `<skeleton>` means the directory that contains this file.

They work for a new project or for an existing one that has outgrown its docs.

## The idea in one paragraph

Cost is roughly **context size × number of calls**, because every call re-reads the whole context. Prompt
caching makes re-reads much cheaper, but not free: cached tokens are still billed, the cache expires between
pauses, and quality drops as context grows. So sessions need to be short (one task, then stop), and they need to
start small: a brief, a short work queue, and docs that get looked up rather than read whole. Knowledge carries
over through files, not through long sessions. Each doc goes in a tier according to how often it needs to be in
context:

| Tier | File | Loaded | Size target | Rule |
|---|---|---|---|---|
| 0 | `CLAUDE.md` | Automatically, on every call | < 5 KB | Fixed rules and pointers only. Never status or history |
| 1 | `PROMPT.md` | Once per session | < 10 KB (35 KB hard max) | Facts, method, **one** task with a "Done when" line. Replace entries, don't add to them |
| 2 | `NEXT.md` | At session start | < 20 KB | Open items only, with stable IDs. Delete finished items; move cold ones to `docs/BACKLOG.md` |
| 3 | `docs/<subsystem>.md`, `src/<area>/CLAUDE.md` | When working on that area | One file per subsystem | Current state at the top, history below |
| 4 | `PROGRESS.md`, `docs/BACKLOG.md`, `docs/LESSONS.md` | Never read whole | Unlimited | Grep only |

## Setup steps

1. **Copy the template** into the project root. Don't overwrite anything already there:
   `cp -rn <skeleton>/template/. <project>/`
   If the project already has its own `CLAUDE.md`, `PROMPT.md`, etc., see "Retrofitting" below.
2. **Learn the project** before you fill anything in. Read the README, the build files and the directory layout;
   for a big tree, use an Explore subagent. Ask the user only about what the code can't tell you: the goal, and
   what "done" looks like for the first milestone.
3. **Fill in `CLAUDE.md`** (tier 0): the one-paragraph description, the real build / test / run commands, the
   layout table and project-specific rules. Delete placeholder rows you have nothing for. Keep it under 5 KB.
4. **Fill in `PROMPT.md`**:
   - Part A: the goal, an architecture sketch and the current state.
   - Part B: the method, and harness rules once there are some.
   - Part C: the **first task**. It must be one task, with a "Done when" line a command can check.
5. **Seed `NEXT.md`** from the user's plan. A multi-priority plan becomes one item per priority, each with its own
   ID and "Done when". Anything not planned for the next few sessions goes to `docs/BACKLOG.md`.
6. **Create subsystem docs** only for areas that already have non-obvious facts. List each one in
   `docs/README.md`. For a large code area, prefer a `CLAUDE.md` in that directory: it loads only when files there
   are touched.
7. **Hook:** the template's `.claude/settings.local.json` registers `~/.claude/hooks/context_guard.py`. Past 250k
   tokens of context, it tells the agent to finish, do the bookkeeping and stop. If that file doesn't exist,
   install it once with `mkdir -p ~/.claude/hooks && ln -s <skeleton>/hooks/context_guard.py ~/.claude/hooks/`.
   If the project already had a `settings.local.json`, the copy in step 1 skipped it. In that case, show the user
   the `hooks` block to merge in by hand: Claude Code doesn't let the agent edit its own settings.
8. **Git:** the copy in step 1 brought along a file named `gitignore` (no dot). Merge its lines into the project's
   `.gitignore` (create it if needed), then delete `gitignore`. By default `CLAUDE.md` stays out of git, as
   personal rules. On a team project where everyone should share the same rules, ask the user whether to commit
   it instead, and drop that line if so. Commit the rest with a plain message ("Add session docs: PROMPT, NEXT,
   PROGRESS, docs index").
9. **Stop.** Report what was filled in, the first task and its "Done when" line. Don't start the first task in the
   setup session. The user starts it fresh with "follow PROMPT.md".

## Retrofitting an existing project

Move content rather than delete it, and keep IDs stable, because commits and other docs refer to them.

- **History in the brief:** session-by-session history in `PROMPT.md` moves to `PROGRESS.md`. Keep only the
  current state.
- **A long gotcha list:** the full list goes to `docs/LESSONS.md` (grep only). `PROMPT.md` keeps the 10 or so that
  come up every session.
- **A big queue:** split `NEXT.md` into active sections (stay) and cold sections (`docs/BACKLOG.md`, same IDs).
  Delete items marked DONE once `PROGRESS.md` records them.
- **"Read X at session start":** change it to "grep X for the task's sections", unless X is in tiers 0–2 and
  within its size target.
- **Check:** before you delete anything from a hot file, list its identifiers (function names, addresses, issue
  numbers, test IDs) and confirm each one still appears in some file, or belongs to finished work.

## Running sessions afterwards

- **Interactive:** start each session with "follow PROMPT.md". When it reports and stops, `/clear` (or open a new
  session) for the next task. Don't keep going in the same session.
- **Unattended:** `scripts/claude-loop.sh` runs one fresh headless session per task. It stops when a `STOP` file
  appears, when a session makes no commit, or after `MAX` runs.
- **A pasted plan with several priorities:** put it into `NEXT.md` as items, then run them one per session.
- **Searching:** multi-file searches go to an Explore subagent. Long jobs run with `run_in_background` or Monitor,
  not `sleep` loops. Screenshots get cropped or downscaled before they're read.
- **Effort:** for mechanical passes (renames, bookkeeping), use lower effort or Sonnet.
