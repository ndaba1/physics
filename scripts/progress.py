#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Build progress.json from git history, logs, exams, and this run's grade.

CI usage (see .github/workflows/grade.yml):

    uv run scripts/progress.py --lean success --notebooks skipped --essays failure \
        --before <sha> --after <sha> --previous prev.json --out progress.json \
        --repo ndaba1/physics --run-url https://github.com/...

Grade values accept GitHub step outcomes (success/failure/skipped/cancelled)
or pass/fail/skipped. With no grade flags the run is "pending" (local preview).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import studylib as sl  # noqa: E402

ZERO_SHA = "0" * 40


def pushed_commits(before: str | None, after: str) -> set[str]:
    if before and before != ZERO_SHA:
        shas = sl.rev_list(f"{before}..{after}")
        if shas:
            return shas
        if sl.rev_list(f"{before}^!") == set():  # `before` unknown (force push): grade only head
            return {after}
        return set()
    return sl.rev_list(after)  # first push of the branch: everything


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lean")
    p.add_argument("--notebooks")
    p.add_argument("--essays")
    p.add_argument("--before", help="sha before the push (github.event.before)")
    p.add_argument("--after", default="HEAD", help="sha after the push (github.sha)")
    p.add_argument("--previous", type=Path, help="previous progress.json to merge day grades from")
    p.add_argument("--out", type=Path, default=Path("progress.json"))
    p.add_argument("--repo", default="ndaba1/physics")
    p.add_argument("--run-url")
    args = p.parse_args()

    lean, notebooks, essays = (sl.normalize_outcome(v) for v in (args.lean, args.notebooks, args.essays))
    status = sl.overall_grade(lean, notebooks, essays)
    grade = {
        "status": status,
        "lean": lean or "skipped",
        "notebooks": notebooks or "skipped",
        "essays": essays or "skipped",
        "runUrl": args.run_url,
    }

    previous = None
    if args.previous and args.previous.exists():
        try:
            previous = json.loads(args.previous.read_text())
        except json.JSONDecodeError as e:
            sl.warn(f"ignoring unreadable {args.previous}: {e}")

    head = sl.git("rev-parse", args.after).strip()
    progress = sl.build_progress(
        commits=sl.load_commits(rev=head),
        logs=sl.load_logs(),
        exams=sl.load_exams(),
        curriculum=sl.load_curriculum(),
        today=sl.today_local(),
        repo=args.repo,
        head_sha=head,
        grade=grade,
        pushed_shas=pushed_commits(args.before, head) if status != "pending" else set(),
        previous=previous,
    )
    args.out.write_text(json.dumps(progress, indent=2, ensure_ascii=False) + "\n")
    s = progress["streak"]
    print(f"wrote {args.out}: grade {status}, streak {s['current']} (longest {s['longest']}), "
          f"{len(progress['days'])} day(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
