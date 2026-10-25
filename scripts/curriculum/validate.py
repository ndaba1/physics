#!/usr/bin/env python3
"""Validate curriculum.json against the v1 contract (SPEC.md). Stdlib only.

Usage: python3 -I validate.py [path/to/curriculum.json]
Exit 0 when every check passes, 1 otherwise.
"""
import json
import os
import sys

LINES = {"PROG", "3D", "ML", "CRYPTO", "PHYS"}
KINDS = {"lean", "notebook", "essay"}
EXPECTED = (
    [f"M0.{i}" for i in range(1, 16)]
    + [f"M1.{i}" for i in range(1, 6)]
    + [f"M2.{i}" for i in range(1, 7)]
    + [f"M3.{i}" for i in range(1, 7)]
    + [f"M4.{i}" for i in range(1, 8)]
)
EXPECTED_MILESTONES = ["M0.a", "M0.b", "M0.c", "M0.d", "M0.e", "M0.f", "M0", "M1", "M2", "M3", "M4", "M5"]


def main(path):
    with open(path, encoding="utf-8") as f:
        cur = json.load(f)
    errors = []
    err = errors.append

    if cur.get("version") != 1:
        err("version must be 1")
    rules = cur.get("rules", [])
    if len(rules) != 10 or not all(isinstance(r, str) and r for r in rules):
        err(f"rules: expected 10 non-empty strings, got {len(rules)}")
    if any("**" in r or "`" in r for r in rules):
        err("rules contain markdown")

    modules = [m for s in cur.get("stages", []) for m in s.get("modules", [])]
    ids = [m["id"] for m in modules]
    idset = set(ids)

    # every Part B module present, ids unique
    for mid in EXPECTED:
        if mid not in idset:
            err(f"missing module {mid}")
    for mid in idset - set(EXPECTED):
        err(f"unexpected module id {mid}")
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        err(f"duplicate module ids: {dups}")

    all_item_ids = []
    for s in cur["stages"]:
        for m in s["modules"]:
            mid = m["id"]
            if m.get("stageId") != s["id"]:
                err(f"{mid}: stageId {m.get('stageId')} != {s['id']}")
            # prereqs reference existing ids
            for p in m.get("prereqs", []):
                if p not in idset:
                    err(f"{mid}: prereq {p} does not exist")
                if p == mid:
                    err(f"{mid}: lists itself as prereq")
            if m.get("deliverableKind") not in KINDS:
                err(f"{mid}: bad deliverableKind {m.get('deliverableKind')}")
            if not isinstance(m.get("weeks"), int) or m["weeks"] < 1:
                err(f"{mid}: weeks must be a positive int")
            exam = m.get("exam") or {}
            if not isinstance(exam.get("text"), str) or exam.get("passMark") not in (65, 70):
                err(f"{mid}: exam needs text and passMark 65/70")
            for c in m.get("core", []):
                if not c.get("title") or not isinstance(c.get("free"), bool):
                    err(f"{mid}: core entry needs title and boolean free: {c}")
                if "url" in c and not str(c["url"]).startswith(("http://", "https://")):
                    err(f"{mid}: bad url {c['url']}")

            derive_ids = [d["id"] for d in m.get("derive", [])]
            build_ids = [b["id"] for b in m.get("build", [])]
            all_item_ids += derive_ids + build_ids
            for d in m.get("derive", []):
                if not d.get("text"):
                    err(f"{d['id']}: empty text")
            # every build line is one of the five
            for b in m.get("build", []):
                if b.get("line") not in LINES:
                    err(f"{b['id']}: bad line {b.get('line')}")
                for l in b.get("lines", []):
                    if l not in LINES:
                        err(f"{b['id']}: bad entry in lines: {l}")
                if not b.get("text"):
                    err(f"{b['id']}: empty text")

            units = m.get("units", [])
            # units sum to weeks (one unit per week, numbered 1..n)
            if len(units) != m.get("weeks"):
                err(f"{mid}: {len(units)} units but weeks = {m.get('weeks')}")
            if [u.get("week") for u in units] != list(range(1, len(units) + 1)):
                err(f"{mid}: unit weeks not numbered 1..n")
            for u in units:
                for k in ("title", "input", "problems"):
                    if not u.get(k):
                        err(f"{mid} week {u.get('week')}: empty {k}")
            if units and "exam" not in units[-1].get("problems", "").lower():
                err(f"{mid}: last unit's problems do not mention the exam")

            # every derive id appears in exactly one unit; builds likewise; no unknown refs
            for key, known, label in (("deriveIds", derive_ids, "derive"), ("buildIds", build_ids, "build")):
                refs = [r for u in units for r in u.get(key, [])]
                for r in refs:
                    if r not in known:
                        err(f"{mid}: unit references unknown {label} id {r}")
                for k in known:
                    n = refs.count(k)
                    if n != 1:
                        err(f"{mid}: {label} id {k} appears in {n} units (expected exactly 1)")

    dup_items = sorted({i for i in all_item_ids if all_item_ids.count(i) > 1})
    if dup_items:
        err(f"duplicate derive/build ids: {dup_items}")

    # prereq graph is acyclic
    graph = {m["id"]: [p for p in m.get("prereqs", []) if p in idset] for m in modules}
    state = {}

    def visit(n, stack):
        if state.get(n) == 1:
            err(f"prereq cycle: {' -> '.join(stack + [n])}")
            return
        if state.get(n) == 2:
            return
        state[n] = 1
        for p in graph[n]:
            visit(p, stack + [n])
        state[n] = 2

    for n in graph:
        visit(n, [])

    # milestones
    ms = cur.get("milestones", [])
    mids = [m["id"] for m in ms]
    if mids != EXPECTED_MILESTONES:
        err(f"milestone ids {mids} != {EXPECTED_MILESTONES}")
    for m in ms:
        for x in m.get("moduleIds", []):
            if x not in idset:
                err(f"milestone {m['id']}: moduleId {x} does not exist")

    n_units = sum(len(m.get("units", [])) for m in modules)
    n_derive = sum(len(m.get("derive", [])) for m in modules)
    n_build = sum(len(m.get("build", [])) for m in modules)
    if errors:
        print(f"FAIL: {len(errors)} problem(s) in {path}")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK: {path}")
    print(f"  stages={len(cur['stages'])} modules={len(modules)} units={n_units} "
          f"derive={n_derive} build={n_build} milestones={len(ms)} rules={len(rules)}")
    for s in cur["stages"]:
        print(f"  {s['id']}: {len(s['modules'])} modules, {sum(m['weeks'] for m in s['modules'])} weeks")
    return 0


if __name__ == "__main__":
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curriculum.json")
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else default))
