#!/usr/bin/env python3
"""Clip engine for Oneware Games' short-form video accounts.

Turns raw gameplay recordings into many platform-ready vertical variants,
plans a posting schedule across the studio's accounts without repeats, and
reports which hooks, games and accounts perform.

  add       register a raw clip in the bank
  variants  render 1080x1920 variants of a clip (hook text, start offset, end card)
  plan      build a posting schedule CSV across active accounts
  report    views by hook / game / platform / account from the posts log

Needs ffmpeg + ffprobe. State lives in marketing/clips/*.csv (tracked);
video files live in clips/ (gitignored). Runs the same on a Mac
(`brew install ffmpeg`) as in the cloud container.
"""

import argparse
import csv
import json
import random
import shutil
import subprocess
import sys
import tempfile
import textwrap
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "marketing" / "clips"
MEDIA = ROOT / "clips"
CATALOG = ROOT / "games" / "catalog.csv"
FONT = next((p for p in (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
) if Path(p).exists()), None)

FIELDS = {
    "bank": ["clip_id", "game", "file", "duration_s", "width", "height",
             "tags", "added", "notes"],
    "variants": ["variant_id", "clip_id", "game", "hook", "start_s",
                 "length_s", "file", "created"],
    "accounts": ["platform", "handle", "scope", "posts_per_day",
                 "post_times", "hashtags", "active"],
    "hooks": ["game", "hook"],
    "posts": ["date", "time", "platform", "account", "variant_id", "clip_id",
              "game", "hook", "caption", "status", "url", "views", "likes",
              "shares", "profile_visits"],
}


# --- state helpers ----------------------------------------------------------

def load(name):
    path = STATE / f"{name}.csv"
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(name, rows):
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / f"{name}.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS[name], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def game_names():
    if not CATALOG.exists():
        return {}
    with CATALOG.open(newline="") as f:
        return {r["slug"]: r["name"] for r in csv.DictReader(f) if r.get("slug")}


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True).stdout
    info = json.loads(out)
    s = info["streams"][0]
    return float(info["format"]["duration"]), int(s["width"]), int(s["height"])


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout
    return bool(out.strip())


def next_id(rows, key, prefix):
    nums = [int(r[key][len(prefix):]) for r in rows
            if r[key].startswith(prefix) and r[key][len(prefix):].isdigit()]
    return f"{prefix}{max(nums, default=0) + 1:04d}"


# --- add --------------------------------------------------------------------

def cmd_add(args):
    bank = load("bank")
    for src in args.files:
        src = Path(src)
        duration, w, h = probe(src)
        clip_id = next_id(bank, "clip_id", "c")
        dest = MEDIA / "raw" / f"{clip_id}{src.suffix.lower()}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        bank.append({
            "clip_id": clip_id, "game": args.game,
            "file": str(dest.relative_to(ROOT)), "duration_s": f"{duration:.2f}",
            "width": w, "height": h, "tags": args.tags or "",
            "added": date.today().isoformat(), "notes": args.notes or "",
        })
        print(f"{clip_id}  {args.game}  {duration:.1f}s  {w}x{h}  <- {src}")
    save("bank", bank)


# --- variants ---------------------------------------------------------------

def _drawtext(textfile, size, y, enable):
    font = f"fontfile='{FONT}':" if FONT else ""
    return (f"drawtext={font}expansion=none:textfile='{textfile}':fontsize={size}:"
            f"fontcolor=white:borderw=6:bordercolor=black@0.85:"
            f"line_spacing=12:text_align=C:x=(w-text_w)/2:y={y}:enable='{enable}'")


def _wrap(text, width):
    return "\n".join(line for para in text.split("\n")
                     for line in textwrap.wrap(para, width) or [""])


def render(src, out, start, length, hook, endcard, hook_secs, audio):
    with tempfile.TemporaryDirectory() as tmp:
        hook_file = Path(tmp) / "hook.txt"
        hook_file.write_text(_wrap(hook.upper(), 18))
        end_file = Path(tmp) / "end.txt"
        end_file.write_text(_wrap(endcard, 22))
        vf = (
            "[0:v]fps=30,split[a][b];"
            "[a]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=24:2[bg];"
            "[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            + _drawtext(hook_file, 78, "h*0.17", f"lt(t,{hook_secs})") + ","
            + _drawtext(end_file, 70, "h*0.58", f"gte(t,{max(length - 2, 0)})")
            + ",format=yuv420p[v]"
        )
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}",
               "-t", f"{length:.2f}", "-i", str(src),
               "-filter_complex", vf, "-map", "[v]"]
        cmd += ["-map", "0:a", "-c:a", "aac", "-b:a", "128k"] if audio else ["-an"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)


def cmd_variants(args):
    bank = {r["clip_id"]: r for r in load("bank")}
    variants = load("variants")
    names = game_names()
    rng = random.Random(args.seed)
    for clip_id in args.clips:
        clip = bank.get(clip_id) or sys.exit(f"error: unknown clip {clip_id}")
        game = clip["game"]
        hooks = args.hooks or [h["hook"] for h in load("hooks") if h["game"] in (game, "*")]
        if not hooks:
            sys.exit(f"error: no hooks for {game}; pass --hooks or add rows "
                     f"to marketing/clips/hooks.csv")
        hooks = rng.sample(hooks, min(args.count, len(hooks)))
        duration = float(clip["duration_s"])
        length = min(args.length, duration)
        # Spread start offsets across the clip so variants look different.
        span = max(duration - length, 0)
        starts = [span * i / max(len(hooks) - 1, 1) for i in range(len(hooks))]
        src = ROOT / clip["file"]
        audio = has_audio(src)
        endcard = args.endcard or f"{names.get(game, game)}\nFree on the App Store"
        for hook, start in zip(hooks, starts):
            vid = next_id(variants, "variant_id", "v")
            out = MEDIA / "out" / game / f"{vid}.mp4"
            out.parent.mkdir(parents=True, exist_ok=True)
            render(src, out, start, length, hook, endcard, args.hook_secs, audio)
            variants.append({
                "variant_id": vid, "clip_id": clip_id, "game": game,
                "hook": hook, "start_s": f"{start:.2f}",
                "length_s": f"{length:.2f}", "file": str(out.relative_to(ROOT)),
                "created": date.today().isoformat(),
            })
            save("variants", variants)  # save per render so a crash keeps progress
            print(f"{vid}  {clip_id}  +{start:.1f}s  {length:.1f}s  \"{hook}\"")


# --- plan -------------------------------------------------------------------

def cmd_plan(args):
    accounts = [a for a in load("accounts") if a.get("active", "yes").lower() == "yes"]
    if not accounts:
        sys.exit("error: no active accounts in marketing/clips/accounts.csv")
    variants = load("variants")
    posts = load("posts")
    names = game_names()
    rng = random.Random(args.seed)

    used_on_account = defaultdict(set)    # handle@platform -> variant ids
    used_on_platform = defaultdict(set)   # platform -> variant ids
    clip_last_used = {}                   # (account, clip) -> date
    hook_views = defaultdict(list)
    for p in posts:
        acct = f"{p['account']}@{p['platform']}"
        used_on_account[acct].add(p["variant_id"])
        used_on_platform[p["platform"]].add(p["variant_id"])
        clip_last_used[(acct, p["clip_id"])] = max(
            clip_last_used.get((acct, p["clip_id"]), ""), p["date"])
        if p.get("views"):
            hook_views[p["hook"]].append(int(p["views"]))
    hook_avg = {h: sum(v) / len(v) for h, v in hook_views.items()}
    # Untested hooks rank like a 75th-percentile hook: ahead of average
    # performers, behind proven winners. No data yet -> all equal.
    explore = args.explore_views
    if explore is None:
        ranked = sorted(hook_avg.values())
        explore = ranked[int(len(ranked) * 0.75)] if ranked else 0

    start = date.fromisoformat(args.start) if args.start else date.today() + timedelta(days=1)
    schedule, shortages = [], defaultdict(int)
    for day in (start + timedelta(days=i) for i in range(args.days)):
        cooldown = (day - timedelta(days=args.clip_cooldown)).isoformat()
        for a in accounts:
            acct = f"{a['handle']}@{a['platform']}"
            times = [t.strip() for t in a["post_times"].split(";") if t.strip()]
            for slot in range(int(a["posts_per_day"])):
                pool = [v for v in variants
                        if (a["scope"] == "studio" or v["game"] == a["scope"])
                        and v["variant_id"] not in used_on_account[acct]
                        and v["variant_id"] not in used_on_platform[a["platform"]]
                        and clip_last_used.get((acct, v["clip_id"]), "") < cooldown]
                if not pool:
                    shortages[acct] += 1
                    continue
                # Proven hooks first, untested hooks next (explore), then random.
                pool.sort(key=lambda v: (-hook_avg.get(v["hook"], explore),
                                         rng.random()))
                v = pool[0]
                used_on_account[acct].add(v["variant_id"])
                used_on_platform[a["platform"]].add(v["variant_id"])
                clip_last_used[(acct, v["clip_id"])] = day.isoformat()
                game_name = names.get(v["game"], v["game"])
                schedule.append({
                    "date": day.isoformat(),
                    "time": times[slot % len(times)] if times else "",
                    "platform": a["platform"], "account": a["handle"],
                    "variant_id": v["variant_id"], "clip_id": v["clip_id"],
                    "game": v["game"], "hook": v["hook"],
                    "caption": f"{v['hook']} — {game_name}, free on the App Store "
                               f"{a.get('hashtags', '')}".strip(),
                    "status": "planned", "file": v["file"],
                })

    out = STATE / f"schedule-{start.isoformat()}.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS["posts"][:10] + ["file"])
        w.writeheader()
        w.writerows(schedule)
    if args.commit:
        save("posts", posts + schedule)
    print(f"{len(schedule)} posts planned over {args.days} days -> {out.relative_to(ROOT)}"
          + ("" if args.commit else "  (dry run: posts log unchanged; add --commit)"))
    for acct, n in sorted(shortages.items()):
        print(f"  short {n} variants for {acct}")
    if shortages:
        print(f"  -> need ~{sum(shortages.values())} more variants "
              f"(about {-(-sum(shortages.values()) // 4)} raw clips at 4 variants each)")


# --- report -----------------------------------------------------------------

def cmd_report(args):
    posts = [p for p in load("posts") if p.get("views")]
    if not posts:
        sys.exit("no posts with views logged yet (fill views in marketing/clips/posts.csv)")
    for dim in ("hook", "game", "platform", "account", "clip_id"):
        groups = defaultdict(list)
        for p in posts:
            groups[p[dim]].append(int(p["views"]))
        print(f"\n## By {dim}\n\n| {dim} | posts | avg views | best |\n|---|---|---|---|")
        for k, v in sorted(groups.items(), key=lambda kv: -sum(kv[1]) / len(kv[1]))[:args.top]:
            print(f"| {k} | {len(v)} | {sum(v) / len(v):.0f} | {max(v)} |")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add", help="register raw clips")
    s.add_argument("files", nargs="+")
    s.add_argument("--game", required=True, help="game slug (or 'studio')")
    s.add_argument("--tags", help="comma-separated, e.g. satisfying,near-miss")
    s.add_argument("--notes")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("variants", help="render vertical variants")
    s.add_argument("clips", nargs="+", help="clip ids")
    s.add_argument("--hooks", nargs="+", help="hook texts (default: hooks.csv)")
    s.add_argument("--count", type=int, default=4, help="variants per clip")
    s.add_argument("--length", type=float, default=12.0, help="seconds")
    s.add_argument("--hook-secs", type=float, default=3.0)
    s.add_argument("--endcard", help="end card text (default: game name + App Store)")
    s.add_argument("--seed", type=int)
    s.set_defaults(fn=cmd_variants)

    s = sub.add_parser("plan", help="build a posting schedule")
    s.add_argument("--days", type=int, default=7)
    s.add_argument("--start", help="YYYY-MM-DD (default: tomorrow)")
    s.add_argument("--clip-cooldown", type=int, default=5,
                   help="days before the same raw clip repeats on an account")
    s.add_argument("--explore-views", type=float,
                   help="assumed views for untested hooks (default: 75th pct of tested)")
    s.add_argument("--commit", action="store_true", help="append to posts log")
    s.add_argument("--seed", type=int)
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser("report", help="performance by hook/game/platform/account")
    s.add_argument("--top", type=int, default=10)
    s.set_defaults(fn=cmd_report)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
