from datetime import date, datetime, timedelta, timezone

import pytest

import studylib as sl

CURRICULUM = {
    "weeklyHoursTarget": 20,
    "dailyMinutesTarget": 180,
    "minimumDay": {"derivations": 1, "problems": 1, "log": True},
    "stages": [{"id": "S0", "modules": [
        {"id": "M0.1", "stageId": "S0", "order": 1, "title": "Proof", "weeks": 2, "prereqs": [],
         "derive": [{"id": "M0.1.d1", "text": "a"}, {"id": "M0.1.d2", "text": "b"}],
         "units": [{"week": 1}, {"week": 2}]},
        {"id": "M0.2", "stageId": "S0", "order": 2, "title": "NT", "weeks": 3, "prereqs": ["M0.1"],
         "derive": [{"id": "M0.2.d1", "text": "c"}], "units": [{"week": 1}, {"week": 2}, {"week": 3}]},
    ]}],
}


def utc(*a):
    return datetime(*a, tzinfo=timezone.utc)


def commit(when, *files, sha=None):
    return sl.Commit(sha=sha or f"{when.isoformat()}{files}", authored=when, files=files)


def log(d, minutes=60, problems=("Hammack 1.1 #1",), **kw):
    return sl.Log(date=d, module=kw.pop("module", "M0.1"), minutes=minutes, problems=list(problems), **kw)


# ---------------------------------------------------------------- day attribution


@pytest.mark.parametrize(("moment", "expected"), [
    (utc(2026, 10, 21, 20, 59), "2026-10-21"),   # 23:59 EAT
    (utc(2026, 10, 21, 21, 0), "2026-10-22"),    # 00:00 EAT next day
    (utc(2026, 10, 22, 2, 0), "2026-10-22"),
    (datetime.fromisoformat("2026-10-22T23:30:00-07:00"), "2026-10-23"),  # authored abroad
    (datetime(2026, 10, 21, 22, 0), "2026-10-22"),  # naive = UTC
])
def test_day_of_uses_nairobi(moment, expected):
    assert sl.day_of(moment).isoformat() == expected


def test_commit_late_utc_lands_on_next_nairobi_day():
    days = sl.build_days([commit(utc(2026, 10, 21, 22, 30), "proofs/Physics/M0_1/A.lean")],
                         {"2026-10-22": log("2026-10-22")}, CURRICULUM)
    assert "2026-10-21" not in days
    assert days["2026-10-22"]["deliverables"]["proofs"] == 1
    assert days["2026-10-22"]["minimumDay"] is True


def test_parse_git_log_drops_deletions():
    text = ("\x1eabc\x1f2026-10-22T10:00:00+03:00\n\nA\tproofs/Physics/M0_1/A.lean\n"
            "D\tnotebooks/M0_1/old.ipynb\nM\tlog/2026-10-22.md\n"
            "\x1edef\x1f2026-10-21T09:00:00+03:00\n")
    a, b = sl.parse_git_log(text)
    assert a.files == ("proofs/Physics/M0_1/A.lean", "log/2026-10-22.md")
    assert a.day == date(2026, 10, 22) and b.files == ()


@pytest.mark.parametrize(("path", "kind"), [
    ("proofs/Physics/M0_1/A.lean", "proofs"),
    ("proofs/lakefile.toml", None),
    ("proofs/.lake/packages/x/Y.lean", None),
    ("notebooks/M0_1/a.ipynb", "notebooks"),
    ("essays/M0_1/a.typ", "essays"),
    ("essays/_template.typ", None),
    ("modules/M0_1/rsa.py", "modules"),
    ("modules/.gitkeep", None),
    ("log/2026-10-22.md", None),
])
def test_classify(path, kind):
    assert sl.classify(path) == kind


# ---------------------------------------------------------------- tiers


def test_minimum_vs_full_day():
    commits = [
        commit(utc(2026, 10, 20, 8), "proofs/Physics/M0_1/A.lean", "log/2026-10-20.md"),
        commit(utc(2026, 10, 21, 8), "notebooks/M0_1/a.ipynb"),
        commit(utc(2026, 10, 22, 8), "modules/M0_1/x.py"),           # build only: no derivation
        commit(utc(2026, 10, 23, 8), "essays/M0_1/a.typ"),
    ]
    logs = {
        "2026-10-20": log("2026-10-20", minutes=150),
        "2026-10-21": log("2026-10-21", minutes=180),
        "2026-10-22": log("2026-10-22", minutes=240),
        "2026-10-23": log("2026-10-23", minutes=200, problems=()),  # no problems
    }
    days = sl.build_days(commits, logs, CURRICULUM)
    assert (days["2026-10-20"]["minimumDay"], days["2026-10-20"]["fullDay"]) == (True, False)
    assert (days["2026-10-21"]["minimumDay"], days["2026-10-21"]["fullDay"]) == (True, True)
    assert (days["2026-10-22"]["minimumDay"], days["2026-10-22"]["fullDay"]) == (False, False)
    assert (days["2026-10-23"]["minimumDay"], days["2026-10-23"]["fullDay"]) == (False, False)
    assert sl.why_not_minimum(days["2026-10-23"], CURRICULUM) == ["log lists no problems"]


def test_deliverable_without_log_is_not_minimum():
    days = sl.build_days([commit(utc(2026, 10, 22, 8), "proofs/Physics/M0_1/A.lean")], {}, CURRICULUM)
    assert days["2026-10-22"]["minimumDay"] is False
    assert days["2026-10-22"]["deliverables"]["log"] is False


def test_same_file_twice_counts_once():
    commits = [commit(utc(2026, 10, 22, 8), "proofs/Physics/M0_1/A.lean"),
               commit(utc(2026, 10, 22, 9), "proofs/Physics/M0_1/A.lean")]
    day = sl.build_days(commits, {}, CURRICULUM)["2026-10-22"]
    assert day["commits"] == 2 and day["deliverables"]["proofs"] == 1


# ---------------------------------------------------------------- streak


def minimum_days(*isos):
    return {d: {"minimumDay": True} for d in isos}


def test_streak_with_gap():
    days = minimum_days("2026-10-10", "2026-10-11", "2026-10-12",  # run of 3
                        "2026-10-15", "2026-10-16")                # gap on 13, 14
    days["2026-10-14"] = {"minimumDay": False}
    s = sl.compute_streak(days, date(2026, 10, 16))
    assert s == {"current": 2, "longest": 3, "lastMinimumDay": "2026-10-16"}


def test_today_not_done_does_not_break_streak():
    days = minimum_days("2026-10-20", "2026-10-21")
    assert sl.compute_streak(days, date(2026, 10, 22))["current"] == 2


def test_missing_yesterday_breaks_streak():
    days = minimum_days("2026-10-19", "2026-10-20")
    s = sl.compute_streak(days, date(2026, 10, 22))
    assert s["current"] == 0 and s["longest"] == 2


def test_empty_streak():
    assert sl.compute_streak({}, date(2026, 10, 22)) == {"current": 0, "longest": 0, "lastMinimumDay": None}


# ---------------------------------------------------------------- week


def test_week_minutes_monday_to_sunday():
    logs = {d: log(d, minutes=m) for d, m in [
        ("2026-10-18", 999),   # Sunday of previous week
        ("2026-10-19", 100),   # Monday
        ("2026-10-22", 150),
        ("2026-10-25", 50),    # Sunday
        ("2026-10-26", 999),   # next Monday
    ]}
    w = sl.week_summary(logs, date(2026, 10, 22), sl.weekly_target_minutes(CURRICULUM))
    assert w == {"start": "2026-10-19", "minutes": 300, "targetMinutes": 1200}


def test_week_start_on_monday_and_sunday():
    assert sl.week_start(date(2026, 10, 19)) == date(2026, 10, 19)
    assert sl.week_start(date(2026, 10, 25)) == date(2026, 10, 19)


# ---------------------------------------------------------------- logs, derivations, modules


def test_parse_log_frontmatter():
    text = """---
date: 2026-10-22
module: M0.1
minutes: 150
problems:
  - "Hammack 1.1 #3"
  - 5
derivation: "√2 is irrational"
derivation_id: M0.1.d1
next_problem: "Hammack 1.2 #4"
brief: >
  Three sentences.
told: false
---

Notes.
"""
    lg = sl.parse_log(text, "2026-10-22")
    assert lg.problems == ["Hammack 1.1 #3", "5"]
    assert lg.minutes == 150 and lg.brief == "Three sentences." and lg.body == "Notes.\n"


def test_parse_log_empty_problems_and_date_mismatch():
    assert sl.parse_log("---\ndate: 2026-10-22\nproblems:\n  # none\n---\n", "2026-10-22").problems == []
    with pytest.raises(sl.LogError):
        sl.parse_log("---\ndate: 2026-10-21\n---\n", "2026-10-22")


def test_next_derivation_skips_used():
    assert sl.next_derivation(CURRICULUM, "M0.1", [])["id"] == "M0.1.d1"
    assert sl.next_derivation(CURRICULUM, "M0.1", ["M0.1.d1"])["id"] == "M0.1.d2"
    assert sl.next_derivation(CURRICULUM, "M0.1", ["M0.1.d1", "M0.1.d2"]) is None


def test_unit_week_and_module_status():
    logs = {"2026-10-01": log("2026-10-01", derivation_id="M0.1.d1"),
            "2026-10-09": log("2026-10-09")}
    assert sl.current_unit_week(logs, CURRICULUM, "M0.1", date(2026, 10, 9)) == 2
    assert sl.current_unit_week(logs, CURRICULUM, "M0.1", date(2026, 12, 1)) == 2  # clamped
    mods = sl.module_summaries(CURRICULUM, logs, [], "M0.1")
    assert mods["M0.1"] == {"status": "active", "daysLogged": 2, "minutes": 120,
                            "deriveDone": 1, "deriveTotal": 2, "examPassed": False}
    assert mods["M0.2"]["status"] == "locked"
    exam = sl.Exam("2026-10-14", "M0.1", "Hammack", 82, 70, True)
    mods = sl.module_summaries(CURRICULUM, logs, [exam], "M0.1")
    assert mods["M0.1"]["status"] == "passed" and mods["M0.2"]["status"] == "available"


# ---------------------------------------------------------------- grade merge


def test_progress_grade_merge():
    old = commit(utc(2026, 10, 21, 8), "proofs/Physics/M0_1/A.lean", sha="old")
    new = commit(utc(2026, 10, 22, 8), "proofs/Physics/M0_1/B.lean", sha="new")
    logs = {"2026-10-21": log("2026-10-21"), "2026-10-22": log("2026-10-22", next_problem="1.2 #4")}
    previous = {"days": {"2026-10-21": {"grade": "pass"}}}
    grade = {"status": "fail", "lean": "fail", "notebooks": "skipped", "essays": "skipped", "runUrl": None}
    p = sl.build_progress(commits=[new, old], logs=logs, exams=[], curriculum=CURRICULUM,
                          today=date(2026, 10, 22), repo="ndaba1/physics", head_sha="new",
                          grade=grade, pushed_shas={"new"}, previous=previous,
                          generated_at=utc(2026, 10, 22, 18))
    assert p["days"]["2026-10-21"]["grade"] == "pass"
    assert p["days"]["2026-10-22"]["grade"] == "fail"
    assert p["generatedAt"] == "2026-10-22T18:00:00Z"
    assert p["streak"]["current"] == 2 and p["nextProblem"] == "1.2 #4"
    assert p["week"]["minutes"] == 120


@pytest.mark.parametrize(("parts", "status"), [
    ((None, None, None), "pending"),
    (("pass", "skipped", "skipped"), "pass"),
    (("pass", "fail", "skipped"), "fail"),
])
def test_overall_grade(parts, status):
    assert sl.overall_grade(*parts) == status


def test_normalize_outcome():
    assert [sl.normalize_outcome(v) for v in ("success", "failure", "skipped", "cancelled", None)] == \
        ["pass", "fail", "skipped", "fail", None]


def test_sample_curriculum_loads():
    import json
    data = json.loads(sl.FIXTURE.read_text())
    assert [m["id"] for m in sl.modules(data)] == ["M0.1", "M0.2"]
    for m in sl.modules(data):
        assert sum(1 for _ in m["units"]) == m["weeks"]
        ids = [i for u in m["units"] for i in u["deriveIds"]]
        assert sorted(ids) == sorted(d["id"] for d in m["derive"])
