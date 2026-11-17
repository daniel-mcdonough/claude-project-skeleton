# Claude Project Skeleton

A project template for [Claude Code](https://claude.com/claude-code) that keeps sessions short and cheap. Each
session does one task, starts from a small brief and hands off to the next session through files instead of a
long conversation.

## The problem

Every API call re-sends the whole context, so cost grows with **context size × number of calls**. Prompt caching
softens this, but cached tokens are still billed, the cache expires when you pause, and long contexts make the
model worse. Long sessions that drift from task to task get expensive and sloppy.

I ran into this on large, long-running projects: forum software, a reimplementation of *1602 A.D.* (*Anno 1602*),
and DragonBox Pyra development (emulator performance work, ports and system applets).

## Why not just let it compact

I used auto-compact for a while. It lost the details that matter most on a long project: how to run the test
harness, local machine settings, things the brief said that the summary decided weren't important. `/compact`
with instructions on what to keep helped, but I never found out how reliable it is, and I don't want to depend on
a summary for facts that have to survive.

I didn't survey other solutions. I built this for my own projects and never had a reason to go looking. Someone
has almost certainly built the same thing, since it's the logical setup. The closest I know of is the "Ralph" loop,
a shell loop that re-runs `claude -p` on a `PROMPT.md`. This version adds stop conditions, tiered docs with size
budgets and a hook that ends sessions cleanly at a context budget.

## The approach

Knowledge carries over through files, not through long sessions. Each doc goes in a tier according to how often
it needs to be in context:

| Tier | File | Loaded |
|---|---|---|
| 0 | `CLAUDE.md` | On every call. Fixed rules and pointers only (< 5 KB) |
| 1 | `PROMPT.md` | Once per session. The brief, and **one** task with a checkable "Done when" line |
| 2 | `NEXT.md` | At session start. Open work items with stable IDs |
| 3 | `docs/<subsystem>.md` | Only when working on that area |
| 4 | `PROGRESS.md`, `docs/BACKLOG.md`, `docs/LESSONS.md` | Never read whole, grep only |

At the end of each session the agent updates the log, the queue and the brief, commits and stops. The next
session starts fresh from those files.

## Requirements

- Claude Code
- Python 3 (for the hook and the stats tool, standard library only)
- bash and git (for the loop script)

## What's here

| Path | What |
|---|---|
| `NEW_PROJECT.md` | Setup instructions, written for a Claude Code session to follow |
| `template/` | The files that get copied into a project |
| `template/scripts/claude-loop.sh` | Runs one fresh headless session per task, unattended |
| `hooks/context_guard.py` | A PostToolUse hook that tells the agent to wrap up once context passes 250k tokens |
| `tools/session_stats.py` | Per-session token stats from your Claude Code transcripts |

## Setup

Clone this repo somewhere, then in your project start Claude Code and say:

> Set up this project using `<path to this repo>/NEW_PROJECT.md`

It works for new projects and for existing ones whose docs have grown too big. The setup session fills in the
templates, picks the first task, symlinks the hook into `~/.claude/hooks/` if it isn't there and stops. After
that, start each session with:

> follow PROMPT.md

and `/clear` when it reports back.

To skip typing the path, you can wrap that first instruction in a user-level skill (`~/.claude/skills/`).

## Configuration

**Hook threshold.** The hook reads `CONTEXT_GUARD_LIMIT` (default 250000) and `CONTEXT_GUARD_STEP` (default
50000). The easiest place to set them is the hook command in `.claude/settings.local.json`:

```json
{ "type": "command", "command": "CONTEXT_GUARD_LIMIT=150000 python3 ~/.claude/hooks/context_guard.py", "timeout": 10 }
```

I don't remember how I picked 250k. It hasn't been tuned, so adjust it to your model and budget.

**Unattended runs.** `MAX` sets the number of runs (default 5), and `CLAUDE_FLAGS` passes extra flags to
`claude`, e.g. `CLAUDE_FLAGS="--model sonnet" scripts/claude-loop.sh`.

## How it works

**The context guard hook** reads the session transcript after each tool call and takes the context size from the
last main-thread API call. Past the limit, it tells the agent to finish its step, do the bookkeeping and stop, and
repeats every `CONTEXT_GUARD_STEP` tokens. It never blocks a tool. State goes in `~/.cache/context_guard/` so each
level only fires once per session.

**The loop script** runs `claude -p "Follow PROMPT.md."` repeatedly, one fresh session per task. It stops when a
`STOP` file appears, when a run fails or makes no commit, or after `MAX` runs. Headless sessions can't answer
permission prompts, so you have to pre-allow the tools they need. Anything you allow, the agent can do with nobody
watching. Keep the allowlist narrow and run it on a branch or in a container.

## Results

I don't have a clean measurement against no system at all. I'd been using a `PROMPT.md` brief for a while before
this template existed, and Claude Code had already deleted the older transcripts. What I can measure is the switch
from that earlier ad-hoc version to this template on two projects. The ad-hoc version let history pile up in
`PROMPT.md` and read `NEXT.md` whole every session.

| Project | Median tokens per session | Median peak context | Sessions over 250k | Worst session |
|---|---|---|---|---|
| Emulator performance work | 17.7M → 4.8M | 231k → 120k | 5 of 14 → 0 of 7 | 535k / 57M → 197k / 11M |
| *1602* reimplementation | 21.9M → 18.8M | 241k → 208k | 5 of 12 → 3 of 28 | 559k / 122M → 274k / 46M |

On *1602*, the overhaul cut the brief from 132 KB to 36 KB and `NEXT.md` from 72 KB to 13 KB. The runaway sessions
stopped: none passed 250k after the first few days. The median barely moved because the later sessions were heavy
mutation-testing batches that run many calls at a steady ~210k context. Their size stays bounded and they get more
done, but they aren't cheap.

To measure your own sessions, run `tools/session_stats.py` (`--project <dir> --split <date>` for a before/after
comparison). Save a baseline before you switch workflows, because old transcripts get deleted.

## Mistakes I made

- **No `NEXT.md` at first.** Open work had nowhere to go but `PROMPT.md`, so the brief bloated. Separating the
  queue from the brief was the first fix.
- **Appending to the brief.** Even with a `NEXT.md`, the *1602* brief grew to 132 KB because each session added
  its history instead of replacing what changed. History now goes to `PROGRESS.md`, which is grep-only.
- **Reading `NEXT.md` whole while it kept growing.** At 72 KB that cost a lot on every session. Finished items now
  get deleted and cold ones move to `docs/BACKLOG.md`.
- **Splitting by date when measuring.** The *1602* overhaul happened mid-afternoon, and a date-only split put the
  worst sessions on the wrong side and made the template look like it made things worse. Use the commit time.

## Troubleshooting

**The hook never fires.**
- Check that `.claude/settings.local.json` exists in the project. Setup copies it with `cp -n`, so an existing file
  is skipped and the `hooks` block has to be merged by hand. The agent can't edit its own settings.
- Check that the symlink resolves with `ls -lL ~/.claude/hooks/context_guard.py`.
- The hook stays silent below the limit. To test it, temporarily set `CONTEXT_GUARD_LIMIT=1000`.

**`settings.local.json` won't commit.** A global gitignore often excludes it (`git check-ignore -v
.claude/settings.local.json` shows the rule). The template's `gitignore` excludes it on purpose. If you want it
committed anyway, use `git add -f`.

**The loop stops after one run with "made no commit".** Usually the session hit a permission it couldn't ask for.
The log in `logs/claude-loop/` shows what it tried.

**`session_stats.py` says "no sessions found".** `--project` has to match the directory you started `claude` in,
not a parent or subdirectory.

## Known issues

- **Budgets creep back.** The *1602* brief went from 36 KB to 40 KB within a week of the overhaul, past the 35 KB
  maximum. Nothing enforces the sizes. Check them now and then.
- **Subsystem docs are unsolved.** I put them in `docs/` and have `CLAUDE.md` point to them. Claude does read them
  when it needs to, but I haven't found a better pattern and don't know if this one scales.
- **The hook threshold isn't tuned** (see Configuration).

## License

MIT
