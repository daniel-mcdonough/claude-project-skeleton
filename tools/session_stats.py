#!/usr/bin/env python3
"""Per-session token stats from Claude Code transcripts (~/.claude/projects/*/*.jsonl).

Prints one CSV row per session: start date, project directory, main-thread API calls, peak context, and total
input tokens processed (cached or not, subagents included). With --split DATE, prints medians for sessions
before and after DATE instead.

  tools/session_stats.py > sessions.csv
  tools/session_stats.py --project ~/git/myproject --split 2026-10-26

Claude Code deletes old transcripts (see cleanupPeriodDays in settings), so save a CSV before you change your
workflow if you want a baseline to compare against.
"""
import argparse, csv, glob, json, os, statistics, sys


def ctx(u):
    return u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)


def session(path):
    calls, total, cwd, start = {}, {}, None, None
    files = [(path, True)] + [(p, False) for p in glob.glob(os.path.join(path[:-6], "subagents", "*.jsonl"))]
    for p, main in files:
        for line in open(p, errors="ignore"):
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") != "assistant" or (main and d.get("isSidechain")):
                continue
            m = d.get("message", {})
            key = (p, m.get("id") or d.get("uuid"))  # streamed messages repeat the same id
            total[key] = m.get("usage") or {}
            if main:
                calls[key] = total[key]
                cwd = cwd or d.get("cwd")
                start = start or d.get("timestamp")
    if len(calls) < 3 or not start:
        return None
    return {"date": start[:10], "project": cwd, "calls": len(calls),
            "peak": max(map(ctx, calls.values())), "tokens": sum(map(ctx, total.values()))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="only sessions whose working directory is this path")
    ap.add_argument("--split", metavar="YYYY-MM-DD", help="print medians before/after this date")
    a = ap.parse_args()
    want = os.path.realpath(os.path.expanduser(a.project)) if a.project else None
    rows = []
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        s = session(f)
        if s and (not want or (s["project"] and os.path.realpath(s["project"]) == want)):
            rows.append(s)
    rows.sort(key=lambda s: s["date"])
    if not rows:
        sys.exit("no sessions found")
    if not a.split:
        w = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
        return
    for label, xs in (("before", [s for s in rows if s["date"] < a.split]),
                      ("after", [s for s in rows if s["date"] >= a.split])):
        if not xs:
            print(f"{label:7s} no sessions")
            continue
        med = lambda k: statistics.median(s[k] for s in xs)
        print(f"{label:7s} sessions={len(xs):4d}  median peak={med('peak') / 1e3:.0f}k  median calls={med('calls'):.0f}"
              f"  median tokens={med('tokens') / 1e6:.1f}M  over 250k={sum(s['peak'] > 250e3 for s in xs)}")


main()
