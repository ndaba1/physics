# physics

Self-study of theoretical physics, from proofs to QFT. This repo is the transcript:
every study day lands here as a commit, CI grades it, and the phone app reads the result.

## Rules

1. Problems are the course. Three lectures ahead of your last problem set: stop, go back.
2. Every module ends with a timed, closed-book exam from a real university. Pass 70% (math), 65% (physics). Fail: redo weak topics, sit a different paper.
3. Every stage ends with a capstone in a public repo.
4. Overlap projects (3D, ML, crypto) are labs attached to a module, finished in 1–3 weekends.
5. Crypto is one module, then a hobby.
6. Story before, original paper after.
7. One derivation per day, even on bad days.
8. Don't jump ahead.
9. Two-week rule: after a two-week gap, don't restart the module. Re-derive one thing, do one problem.
10. Never end a session without knowing the next problem. "Do 4.7", not "continue chapter 4".

The full list lives in `curriculum.json` (`rules`).

## The daily loop

| Block | Minutes | What |
|---|---|---|
| Input | 20 | Read or watch the unit's input. Stop at the first problem you can attempt. |
| Problems | 90 | Work problems. Write each id into `problems:` as you go. |
| Derivation | 30 | The derivation of the day, as a Lean proof, a notebook, or an essay. |
| Build | 30 | The module's build project under `modules/<ModuleDir>/`. |
| Log + brief | 10 | Fill the log. Write `next_problem`. Write three sentences for tonight. |

Total 180 minutes. Target 20 hours a week.

## Two tiers

- **minimumDay**: one derivation deliverable committed (`proofs/**/*.lean`, `notebooks/**/*.ipynb`, or `essays/**/*.typ`) and `log/YYYY-MM-DD.md` lists at least one problem. This keeps the streak.
- **fullDay**: minimumDay and `minutes: 180` or more. Nice to have; never affects the streak.

Days are Africa/Nairobi calendar days, taken from each commit's author timestamp.
The streak counts back from today, or from yesterday if today isn't done yet.
`modules/` commits count as commits but not as derivations.

## Layout

```
curriculum.json                    compiled curriculum (modules, derive/build items, units)
log/YYYY-MM-DD.md                  one per study day; template: log/_template.md
exams/YYYY-MM-DD-<moduleId>.md     one per exam sat; template: exams/_template.md
proofs/Physics/<ModuleDir>/*.lean  Lean 4 + Mathlib (lake project in proofs/)
notebooks/<ModuleDir>/*.ipynb      must execute top to bottom
essays/<ModuleDir>/*.typ           must compile; import essays/_template.typ
modules/<ModuleDir>/               build projects (not graded)
scripts/day                        the daily CLI
scripts/progress.py                builds progress.json
```

`<ModuleDir>` is the module id with dots replaced: `M0.1` → `M0_1`. Lean namespaces can't contain dots.

## The log

```yaml
---
date: 2026-10-22
module: M0.1
minutes: 150
problems:
  - "Hammack 1.1 #3"
  - "Hammack 1.1 #5"
derivation: "√2 is irrational"
derivation_id: "M0.1.d1"            # set by `day start`; marks the derive item as used
deliverable: proofs/Physics/M0_1/Sqrt2Irrational.lean
stuck: "Strong induction vs ordinary induction, when each"
next_problem: "Hammack 1.2 #4"      # required to end the day
brief: >
  Three sentences to say to my partner tonight.
told: false                         # flip once said
---

Free-form notes.
```

## `scripts/day`

Run from the repo root.

```sh
uv run scripts/day start [--module M0.1]   # create today's log
uv run scripts/day status                  # streak, today's tier, hours this week
uv run scripts/day end [--no-push]         # validate, commit everything, push
```

- `start` copies `log/_template.md` to today's date. It takes the module from `--module` or the last log, puts the last log's `next_problem` under `## Start here`, and picks the derivation of the day: the first `derive` item of the module whose id no log has used yet. It prints the unit's input and problems.
- `end` refuses if `next_problem` or `problems` is empty. It warns when no derivation deliverable is committed or pending today. Then `git add -A`, `git commit -m "day(M0.1): <derivation>"`, `git push`.
- `status` runs the same code as CI (`scripts/studylib.py`) against local git and logs.

If `curriculum.json` is missing, both scripts fall back to `scripts/fixtures/curriculum.sample.json` and print a warning.

Tests: `uv run pytest`.

## Local checks

```sh
cd proofs && lake exe cache get && lake build
uv run jupyter nbconvert --to notebook --execute --output-dir /tmp notebooks/M0_1/induction_invariants.ipynb
typst compile --root essays essays/M0_1/what-i-learned.typ /tmp/out.pdf
```

## How CI grades

`.github/workflows/grade.yml` runs on every push to `main` and on manual dispatch.

1. **Lean**: `lake exe cache get && lake build` in `proofs/` (leanprover/lean-action).
2. **Notebooks**: executes the notebooks changed in the push (all of them on manual dispatch). 600 s per cell.
3. **Essays**: `typst compile` on every `.typ` under `essays/`.
4. **Always**: `scripts/progress.py` builds `progress.json` and commits it to the orphan branch `data`.

A grader that has nothing to check reports `skipped`. Any `fail` turns the run red. The days touched by the push get this run's grade. Older days keep the grade from the previous `progress.json`.

## Where the app reads

- Curriculum: `https://raw.githubusercontent.com/ndaba1/physics/main/curriculum.json`
- Progress: `https://raw.githubusercontent.com/ndaba1/physics/data/progress.json`

The app writes only to today's log (`brief`, `told`, `next_problem`, `minutes`) through the GitHub Contents API.
