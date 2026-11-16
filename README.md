# claude-project-skeleton

A project template for [Claude Code](https://claude.com/claude-code) that keeps sessions short and cheap. Each
session does one task, starts from a small brief and hands off to the next session through files instead of a
long conversation.

## Why

Every API call re-sends the whole context, so cost grows with **context size × number of calls**. Prompt caching
softens this, but cached tokens are still billed, the cache expires when you pause, and long contexts make the
model worse. Long sessions that drift from task to task get expensive and sloppy.

The fix is to put each doc in a tier according to how often it needs to be in context:

| Tier | File | Loaded |
|---|---|---|
| 0 | `CLAUDE.md` | On every call. Fixed rules and pointers only (< 5 KB) |
| 1 | `PROMPT.md` | Once per session. The brief, and **one** task with a checkable "Done when" line |
| 2 | `NEXT.md` | At session start. Open work items with stable IDs |
| 3 | `docs/<subsystem>.md` | Only when working on that area |
| 4 | `PROGRESS.md`, `docs/BACKLOG.md`, `docs/LESSONS.md` | Never read whole, grep only |

At the end of each session the agent updates the log, the queue and the brief, commits and stops. The next
session starts fresh from those files.

## Background

I built this while working on large, long-running projects: forum software, a reimplementation of *1602 A.D.*
(*Anno 1602*), and DragonBox Pyra development (emulator performance work, ports and system applets). On those,
long sessions kept getting slow, expensive and confused. I later found that others had landed on similar ideas,
notably the "Ralph" loop (a shell loop re-running `claude -p` on a `PROMPT.md`). This version adds stop
conditions, tiered docs with size budgets and a hook that ends sessions cleanly at a context budget.

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

To measure your own sessions, run `tools/session_stats.py`. Save a baseline before you switch workflows,
because old transcripts get deleted.

## What's here

| Path | What |
|---|---|
| `NEW_PROJECT.md` | Setup instructions, written for a Claude Code session to follow |
| `template/` | The files that get copied into a project |
| `template/scripts/claude-loop.sh` | Runs one fresh headless session per task, unattended |
| `hooks/context_guard.py` | A PostToolUse hook that tells the agent to wrap up once context passes 250k tokens |
| `tools/session_stats.py` | Per-session token stats from your Claude Code transcripts |

## Usage

Clone this repo somewhere, then in your project start Claude Code and say:

> Set up this project using `<path to this repo>/NEW_PROJECT.md`

It works for new projects and for existing ones whose docs have grown too big. The setup session fills in the
templates, picks the first task, installs the hook if needed and stops. After that, start each session with:

> follow PROMPT.md

and `/clear` when it reports back.

To skip typing the path, you can wrap that first instruction in a user-level skill (`~/.claude/skills/`).

### The context guard hook

`hooks/context_guard.py` reads the session transcript after each tool call. Once context passes
`CONTEXT_GUARD_LIMIT` tokens (default 250000), it tells the agent to finish its step, do the bookkeeping and stop,
and repeats every `CONTEXT_GUARD_STEP` tokens (default 50000). It never blocks a tool. Setup symlinks it to
`~/.claude/hooks/context_guard.py`, the path the template's `.claude/settings.local.json` points to.

### Unattended runs

`scripts/claude-loop.sh` (copied into your project) runs `claude -p "Follow PROMPT.md."` repeatedly, one fresh
session per task. It stops when a `STOP` file appears, when a run fails or makes no commit, or after `MAX` runs.

Headless sessions can't answer permission prompts, so you have to pre-allow the tools they need. Anything you
allow, the agent can do with nobody watching. Keep the allowlist narrow and run it on a branch or in a container.

## License

MIT
