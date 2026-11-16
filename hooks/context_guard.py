#!/usr/bin/env python3
"""PostToolUse hook: tell the agent to wrap up once the session's context gets large.

Reads the context size of the latest main-thread API call from the transcript. Past LIMIT tokens it
adds a note to the agent's context, then again every STEP tokens after that. Never blocks a tool.
Env: CONTEXT_GUARD_LIMIT (default 250000), CONTEXT_GUARD_STEP (default 50000).
"""
import json, os, sys

LIMIT = int(os.environ.get("CONTEXT_GUARD_LIMIT", 250_000))
STEP = int(os.environ.get("CONTEXT_GUARD_STEP", 50_000))
STATE_DIR = os.path.expanduser("~/.cache/context_guard")


def last_context(path):
    with open(path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        for chunk in (1 << 19, 1 << 23, size):
            f.seek(max(0, size - chunk))
            lines = f.read().splitlines()
            for line in reversed(lines):
                if b'"usage"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") != "assistant" or d.get("isSidechain"):
                    continue
                u = d.get("message", {}).get("usage") or {}
                return (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                        + u.get("cache_creation_input_tokens", 0))
            if chunk >= size:
                break
    return 0


def main():
    try:
        hook = json.load(sys.stdin)
        ctx = last_context(hook["transcript_path"])
    except Exception:
        return
    if ctx < LIMIT:
        return
    level = (ctx - LIMIT) // STEP
    os.makedirs(STATE_DIR, exist_ok=True)
    state = os.path.join(STATE_DIR, hook.get("session_id", "unknown"))
    try:
        last = int(open(state).read())
    except (OSError, ValueError):
        last = -1
    if level <= last:
        return
    open(state, "w").write(str(level))
    note = (f"Context is now about {ctx // 1000}k tokens (over the {LIMIT // 1000}k session budget). "
            "Finish the step you are on, then do the end-of-session bookkeeping your brief describes "
            "(PROMPT.md / NEXT.md / PROGRESS.md, commit), give the short report and stop. "
            "Don't start another task: the next session continues from those files at a fraction of the cost.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": note}}))


main()
