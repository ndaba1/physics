"""Shared logic for `scripts/day` and `scripts/progress.py`.

Everything that decides whether a day counts lives here, so the local CLI and
the CI grader can never disagree. Pure functions take plain data (commits,
logs, curriculum, today's date); the thin I/O helpers at the bottom read the
repo.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import yaml

TZ = ZoneInfo("Africa/Nairobi")
ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = "curriculum.json"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "curriculum.sample.json"

DERIVATION_KINDS = ("proofs", "notebooks", "essays")
DELIVERABLE_KINDS = (*DERIVATION_KINDS, "modules")
LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


# --------------------------------------------------------------------------- dates


def day_of(moment: datetime) -> date:
    """Calendar date of `moment` in Africa/Nairobi. Naive datetimes are UTC."""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(TZ).date()


def today_local(now: datetime | None = None) -> date:
    return day_of(now or datetime.now(timezone.utc))


def week_start(d: date) -> date:
    """Monday of the ISO week containing `d`."""
    return d - timedelta(days=d.weekday())


def module_dir(module_id: str) -> str:
    """Directory name for a module id: `M0.1` -> `M0_1` (Lean namespaces cannot hold dots)."""
    return module_id.replace(".", "_")


# --------------------------------------------------------------------------- commits


@dataclass(frozen=True)
class Commit:
    sha: str
    authored: datetime  # timezone-aware
    files: tuple[str, ...] = ()

    @property
    def day(self) -> date:
        return day_of(self.authored)


def classify(path: str) -> str | None:
    """Which deliverable bucket a changed file falls in, or None.

    Only real artefacts count: `.lean` under proofs/ (not the lake config),
    `.ipynb` under notebooks/, `.typ` under essays/, anything under modules/.
    Files whose name starts with `_` (templates) and `.gitkeep` never count.
    """
    parts = path.split("/")
    name = parts[-1]
    if name.startswith("_") or name == ".gitkeep" or len(parts) < 2:
        return None
    top = parts[0]
    if top == "proofs" and name.endswith(".lean") and ".lake" not in parts:
        return "proofs"
    if top == "notebooks" and name.endswith(".ipynb") and ".ipynb_checkpoints" not in parts:
        return "notebooks"
    if top == "essays" and name.endswith(".typ"):
        return "essays"
    if top == "modules":
        return "modules"
    return None


GIT_FORMAT = "%x1e%H%x1f%aI"


def parse_git_log(text: str) -> list[Commit]:
    """Parse `git log --name-status --format=GIT_FORMAT` output.

    Deleted files are dropped: removing a proof is not a deliverable.
    """
    commits = []
    for chunk in text.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        header, *rest = chunk.split("\n")
        sha, iso = header.split("\x1f")
        files = []
        for line in rest:
            if not line.strip():
                continue
            status, _, path = line.partition("\t")
            if not path:  # plain --name-only output
                files.append(status)
            elif not status.startswith("D"):
                files.append(path)
        files = tuple(files)
        commits.append(Commit(sha=sha, authored=datetime.fromisoformat(iso), files=files))
    return commits


# --------------------------------------------------------------------------- logs


class LogError(ValueError):
    pass


@dataclass
class Log:
    date: str
    module: str = ""
    minutes: int = 0
    problems: list[str] = field(default_factory=list)
    derivation: str = ""
    derivation_id: str = ""
    deliverable: str = ""
    stuck: str = ""
    next_problem: str = ""
    brief: str = ""
    told: bool = False
    body: str = ""


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise LogError("missing frontmatter (file must start with ---)")
    parts = re.split(r"^---[ \t]*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        raise LogError("unterminated frontmatter")
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise LogError(f"bad YAML: {e}") from e
    if not isinstance(data, dict):
        raise LogError("frontmatter is not a mapping")
    return data, parts[2].lstrip("\n")


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def parse_log(text: str, date_str: str) -> Log:
    data, body = split_frontmatter(text)
    fm_date = _s(data.get("date"))
    if fm_date and fm_date != date_str:
        raise LogError(f"frontmatter date {fm_date} does not match file name {date_str}")
    problems = data.get("problems") or []
    if isinstance(problems, str):
        problems = [problems]
    try:
        minutes = int(data.get("minutes") or 0)
    except (TypeError, ValueError) as e:
        raise LogError(f"minutes must be a number, got {data.get('minutes')!r}") from e
    return Log(
        date=date_str,
        module=_s(data.get("module")),
        minutes=max(minutes, 0),
        problems=[_s(p) for p in problems if _s(p)],
        derivation=_s(data.get("derivation")),
        derivation_id=_s(data.get("derivation_id")),
        deliverable=_s(data.get("deliverable")),
        stuck=_s(data.get("stuck")),
        next_problem=_s(data.get("next_problem")),
        brief=_s(data.get("brief")),
        told=bool(data.get("told")),
        body=body,
    )


@dataclass
class Exam:
    date: str
    moduleId: str
    paper: str
    score: float
    passMark: float
    passed: bool

    def to_json(self) -> dict[str, Any]:
        return self.__dict__.copy()


def parse_exam(text: str, name: str) -> Exam:
    data, _ = split_frontmatter(text)
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", name)
    d = _s(data.get("date")) or (m.group(1) if m else "")
    module = _s(data.get("module")) or (m.group(2) if m else "")
    score = float(data.get("score") or 0)
    pass_mark = float(data.get("pass_mark") or 70)
    passed = data.get("passed")
    passed = bool(passed) if passed is not None else score >= pass_mark
    return Exam(d, module, _s(data.get("paper")), score, pass_mark, passed)


# --------------------------------------------------------------------------- curriculum


def modules(curriculum: dict) -> list[dict]:
    out = [m for s in curriculum.get("stages", []) for m in s.get("modules", [])]
    return sorted(out, key=lambda m: (m.get("stageId", ""), m.get("order", 0)))


def find_module(curriculum: dict, module_id: str) -> dict | None:
    return next((m for m in modules(curriculum) if m["id"] == module_id), None)


def daily_target(curriculum: dict) -> int:
    return int(curriculum.get("dailyMinutesTarget", 180))


def weekly_target_minutes(curriculum: dict) -> int:
    return int(curriculum.get("weeklyHoursTarget", 20)) * 60


def next_derivation(curriculum: dict, module_id: str, used: Iterable[str]) -> dict | None:
    """First derive item of the module whose id has not been used in any log."""
    module = find_module(curriculum, module_id)
    used = set(used)
    if not module:
        return None
    return next((d for d in module.get("derive", []) if d["id"] not in used), None)


# --------------------------------------------------------------------------- grading


def build_days(
    commits: Iterable[Commit], logs: dict[str, Log], curriculum: dict
) -> dict[str, dict[str, Any]]:
    """Per-day records (progress.json `days`, without `grade`)."""
    rules = curriculum.get("minimumDay", {})
    need_derivations = int(rules.get("derivations", 1))
    need_problems = int(rules.get("problems", 1))
    need_log = bool(rules.get("log", True))
    target = daily_target(curriculum)

    per_day: dict[str, dict[str, Any]] = {}

    def slot(d: str) -> dict[str, Any]:
        return per_day.setdefault(d, {"commits": 0, "files": {k: set() for k in DELIVERABLE_KINDS}})

    for c in commits:
        s = slot(c.day.isoformat())
        s["commits"] += 1
        for f in c.files:
            kind = classify(f)
            if kind:
                s["files"][kind].add(f)
    for d in logs:
        slot(d)

    days = {}
    for d in sorted(per_day):
        s = per_day[d]
        log = logs.get(d)
        deliverables: dict[str, Any] = {k: len(s["files"][k]) for k in DELIVERABLE_KINDS}
        deliverables["log"] = log is not None
        derivations = sum(deliverables[k] for k in DERIVATION_KINDS)
        problems = len(log.problems) if log else 0
        minutes = log.minutes if log else 0
        minimum = (
            derivations >= need_derivations
            and problems >= need_problems
            and (log is not None or not need_log)
        )
        days[d] = {
            "commits": s["commits"],
            "deliverables": deliverables,
            "minutes": minutes,
            "problems": problems,
            "moduleId": log.module if log else None,
            "derivation": log.derivation if log else None,
            "derivationId": (log.derivation_id or None) if log else None,
            "nextProblem": log.next_problem if log else None,
            "brief": log.brief if log else None,
            "told": log.told if log else False,
            "minimumDay": minimum,
            "fullDay": minimum and minutes >= target,
        }
    return days


def why_not_minimum(day: dict[str, Any] | None, curriculum: dict) -> list[str]:
    """Human-readable reasons a day is not (yet) a minimumDay."""
    rules = curriculum.get("minimumDay", {})
    if day is None:
        return ["no log and no commits today"]
    reasons = []
    derivations = sum(day["deliverables"][k] for k in DERIVATION_KINDS)
    if derivations < int(rules.get("derivations", 1)):
        reasons.append("no committed .lean / .ipynb / .typ deliverable")
    if not day["deliverables"]["log"]:
        reasons.append("no log file")
    elif day["problems"] < int(rules.get("problems", 1)):
        reasons.append("log lists no problems")
    return reasons


def compute_streak(days: dict[str, dict[str, Any]], today: date) -> dict[str, Any]:
    good = {date.fromisoformat(d) for d, r in days.items() if r["minimumDay"]}
    cursor = today if today in good else today - timedelta(days=1)
    current = 0
    while cursor in good:
        current += 1
        cursor -= timedelta(days=1)
    longest = run = 0
    prev = None
    for d in sorted(good):
        run = run + 1 if prev is not None and d - prev == timedelta(days=1) else 1
        longest = max(longest, run)
        prev = d
    return {
        "current": current,
        "longest": longest,
        "lastMinimumDay": max(good).isoformat() if good else None,
    }


def week_summary(logs: dict[str, Log], today: date, target_minutes: int) -> dict[str, Any]:
    start = week_start(today)
    end = start + timedelta(days=6)
    minutes = sum(
        log.minutes for d, log in logs.items() if start <= date.fromisoformat(d) <= end
    )
    return {"start": start.isoformat(), "minutes": minutes, "targetMinutes": target_minutes}


def latest_log(logs: dict[str, Log], before: str | None = None) -> Log | None:
    keys = sorted(d for d in logs if before is None or d < before)
    return logs[keys[-1]] if keys else None


def used_derive_ids(logs: dict[str, Log]) -> list[str]:
    seen: list[str] = []
    for d in sorted(logs):
        i = logs[d].derivation_id
        if i and i not in seen:
            seen.append(i)
    return seen


def current_module_id(logs: dict[str, Log], curriculum: dict) -> str | None:
    last = next((logs[d] for d in sorted(logs, reverse=True) if logs[d].module), None)
    if last:
        return last.module
    mods = modules(curriculum)
    return mods[0]["id"] if mods else None


def current_unit_week(logs: dict[str, Log], curriculum: dict, module_id: str | None, today: date) -> int:
    """1 + whole weeks since the first log for the module, clamped to the module's units."""
    if not module_id:
        return 1
    dates = sorted(d for d, log in logs.items() if log.module == module_id)
    module = find_module(curriculum, module_id) or {}
    n_units = len(module.get("units", [])) or int(module.get("weeks", 1)) or 1
    if not dates:
        return 1
    week = 1 + (today - date.fromisoformat(dates[0])).days // 7
    return max(1, min(week, n_units))


def module_summaries(
    curriculum: dict, logs: dict[str, Log], exams: list[Exam], current: str | None
) -> dict[str, dict[str, Any]]:
    used = set(used_derive_ids(logs))
    passed = {e.moduleId for e in exams if e.passed}
    out = {}
    for m in modules(curriculum):
        mid = m["id"]
        mlogs = [log for log in logs.values() if log.module == mid]
        derive_ids = [d["id"] for d in m.get("derive", [])]
        if mid in passed:
            status = "passed"
        elif mid == current:
            status = "active"
        elif all(p in passed for p in m.get("prereqs", [])):
            status = "available"
        else:
            status = "locked"
        out[mid] = {
            "status": status,
            "daysLogged": len(mlogs),
            "minutes": sum(log.minutes for log in mlogs),
            "deriveDone": sum(1 for i in derive_ids if i in used),
            "deriveTotal": len(derive_ids),
            "examPassed": mid in passed,
        }
    return out


OUTCOME = {"success": "pass", "pass": "pass", "failure": "fail", "fail": "fail",
           "cancelled": "fail", "skipped": "skipped", "": "skipped"}


def normalize_outcome(value: str | None) -> str | None:
    """Map a GitHub step outcome (success/failure/skipped/cancelled) to pass/fail/skipped."""
    if value is None:
        return None
    return OUTCOME.get(value.strip().lower(), "fail")


def overall_grade(lean: str | None, notebooks: str | None, essays: str | None) -> str:
    parts = [lean, notebooks, essays]
    if all(p is None for p in parts):
        return "pending"
    if any(p == "fail" for p in parts):
        return "fail"
    return "pass"


def build_progress(
    *,
    commits: list[Commit],
    logs: dict[str, Log],
    exams: list[Exam],
    curriculum: dict,
    today: date,
    repo: str,
    head_sha: str | None,
    grade: dict[str, Any],
    pushed_shas: set[str] | None,
    previous: dict | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Assemble progress.json.

    Days touched by `pushed_shas` take this run's grade; other days keep the
    grade they had in `previous` (the last progress.json), else "pending".
    """
    days = build_days(commits, logs, curriculum)
    prev_days = (previous or {}).get("days", {})
    pushed_days = {c.day.isoformat() for c in commits if pushed_shas and c.sha in pushed_shas}
    for d, rec in days.items():
        if d in pushed_days and grade["status"] != "pending":
            rec["grade"] = grade["status"]
        else:
            rec["grade"] = prev_days.get(d, {}).get("grade", "pending")

    current = current_module_id(logs, curriculum)
    last = latest_log(logs)
    return {
        "version": 1,
        "generatedAt": (generated_at or datetime.now(timezone.utc))
        .astimezone(timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": repo,
        "headSha": head_sha,
        "grade": grade,
        "currentModuleId": current,
        "currentUnitWeek": current_unit_week(logs, curriculum, current, today),
        "nextProblem": last.next_problem if last else None,
        "usedDeriveIds": used_derive_ids(logs),
        "streak": compute_streak(days, today),
        "week": week_summary(logs, today, weekly_target_minutes(curriculum)),
        "days": days,
        "exams": [e.to_json() for e in sorted(exams, key=lambda e: e.date)],
        "modules": module_summaries(curriculum, logs, exams, current),
    }


# --------------------------------------------------------------------------- repo I/O


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)


def load_curriculum(root: Path = ROOT) -> dict:
    path = root / CURRICULUM
    if not path.exists():
        warn(f"{CURRICULUM} missing; using {FIXTURE.relative_to(ROOT)}")
        path = FIXTURE
    return json.loads(path.read_text())


def load_logs(root: Path = ROOT) -> dict[str, Log]:
    logs = {}
    for p in sorted((root / "log").glob("*.md")):
        m = LOG_NAME.match(p.name)
        if not m:
            continue
        try:
            logs[m.group(1)] = parse_log(p.read_text(), m.group(1))
        except LogError as e:
            warn(f"skipping {p.relative_to(root)}: {e}")
    return logs


def load_exams(root: Path = ROOT) -> list[Exam]:
    exams = []
    for p in sorted((root / "exams").glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            exams.append(parse_exam(p.read_text(), p.name))
        except (LogError, ValueError) as e:
            warn(f"skipping {p.relative_to(root)}: {e}")
    return exams


def git(*args: str, root: Path = ROOT) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout


def load_commits(root: Path = ROOT, rev: str = "HEAD") -> list[Commit]:
    try:
        out = git("log", rev, "--no-renames", "--name-status",
                  f"--format={GIT_FORMAT}", root=root)
    except subprocess.CalledProcessError:
        return []  # no commits yet
    return parse_git_log(out)


def rev_list(spec: str, root: Path = ROOT) -> set[str]:
    try:
        return set(git("rev-list", spec, root=root).split())
    except subprocess.CalledProcessError:
        return set()
