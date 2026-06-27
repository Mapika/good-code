#!/usr/bin/env python3
"""Measure code-quality TRIPWIRES for the good-code skill.

These are descriptive signals, NOT targets. Per the eval design, a skill that
games any single number (e.g. drives comment ratio to zero) is failing, so this
tool reports a spread and is meant to be read by a human, never optimized against.

Backends are optional and shelled out to (not imported), so this runs under the
system Python even when the tools live in isolated uv/npx environments:
  - lizard  (cross-language cyclomatic complexity, NLOC, params, fn length)
  - radon   (Python maintainability index)
  - jscpd   (cross-language copy/paste duplication; via npx)
Anything missing degrades to a pure-Python estimate and an install hint.

Usage:
  measure.py PATH [PATH ...]            # report metrics for the given files/dirs
  measure.py --json PATH                # machine-readable output
  measure.py --compare BASE CAND        # diff two trees (skill vs no-skill arm)
  measure.py --no-dup PATH              # skip duplication (faster)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Make tools installed by `uv tool install` / `go install` discoverable without
# the caller having to fix up PATH first.
for extra in (os.path.expanduser("~/.local/bin"), os.path.expanduser("~/go/bin")):
    if os.path.isdir(extra) and extra not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = extra + os.pathsep + os.environ.get("PATH", "")

CODE_EXT = {".py": "python", ".ts": "ts", ".tsx": "ts", ".js": "js", ".jsx": "js", ".go": "go"}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", "__pycache__", ".venv", ".next"}

# Complexity thresholds for "how many functions cross the line" — classic McCabe
# territory, not hard limits. A function over these is worth a second look, not a
# rewrite (see rule size-follows-cohesion: length follows cohesion, not a cap).
CCN_WARN = 10
LEN_WARN = 60
PARAM_WARN = 5

# Keep each backend invocation well under ARG_MAX on huge repos (the file list is
# passed on the command line). Batches are merged after.
ARG_BATCH = 300

# Heuristic anti-pattern scanners, each tied to a skill rule and SCOPED to the
# languages where the pattern is meaningful (so Go's idiomatic `any` builtin and
# Python's `//` floor-division never trip a TS rule). Regex is lossy, so hits are
# "smells to check", reported with file:line, never failures. Patterns run against
# whole-file text (re.M) so multi-line forms like `except Exception:\n  pass` and
# a `catch (e) {\n}` are caught, not just the single-line versions.
SMELLS = [
    ("handle-errors-dont-swallow", {"python"},
     re.compile(r"^[ \t]*except\b[^\n:]*:[ \t]*(?:#[^\n]*)?\n[ \t]*(?:pass|return\s+None)\b", re.M)),
    ("handle-errors-dont-swallow", {"ts", "js"},
     re.compile(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}")),
    ("types-at-boundaries-no-escape-hatches", {"ts", "js"},
     re.compile(r"\bas\s+any\b|:\s*any\b|@ts-ignore|@ts-nocheck")),
    ("match-surrounding-style", {"python", "ts", "js", "go"},
     re.compile(r"eslint-disable|#\s*noqa|#\s*type:\s*ignore")),
]


def batches(seq: list, n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def lang_of(path: str) -> str:
    return CODE_EXT[os.path.splitext(path)[1]]


def discover(path: str) -> list[str]:
    if os.path.isfile(path):
        return [path] if os.path.splitext(path)[1] in CODE_EXT else []
    found = []
    for base, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1] in CODE_EXT:
                found.append(os.path.join(base, f))
    return found


def have(tool: str) -> bool:
    """Is a backend actually installed? (npx ships with node.)"""
    if tool == "jscpd":
        return shutil.which("npx") is not None
    return shutil.which(tool) is not None


def run(cmd: list[str], timeout: int = 180) -> tuple[int, str]:
    """Run a backend tool; return (rc, stdout). rc=-1 means it could not run."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout
    # OSError covers ARG_MAX (E2BIG), non-executable backend (PermissionError),
    # and missing binary (FileNotFoundError) — none should crash the whole tool.
    except (subprocess.TimeoutExpired, OSError):
        return -1, ""


def lizard_metrics(files: list[str]) -> dict | None:
    if not have("lizard"):
        return None
    # --csv columns: nloc,ccn,token,param,length,location,file,fn,long_name,start,end
    rows: list[str] = []
    for chunk in batches(files, ARG_BATCH):
        rc, out = run(["lizard", "--csv", *chunk])
        if rc == 0 and out:
            rows.extend(out.splitlines())
    ccns, lengths, params, complex_fns = [], [], [], []
    for cols in csv.reader(rows):  # csv.reader handles commas inside quoted long_name
        if len(cols) < 8:
            continue
        try:
            _nloc, ccn, _tok, param, length = (int(cols[i]) for i in range(5))
        except ValueError:
            continue  # malformed / unexpected row
        ccns.append(ccn); lengths.append(length); params.append(param)
        if ccn > CCN_WARN or length > LEN_WARN or param > PARAM_WARN:
            complex_fns.append({"fn": cols[7], "file": cols[6], "ccn": ccn, "length": length, "params": param})
    if not ccns:
        return {"functions": 0, "complex_functions": []}
    return {
        "functions": len(ccns),
        "ccn_avg": round(sum(ccns) / len(ccns), 2),
        "ccn_max": max(ccns),
        "fn_len_avg": round(sum(lengths) / len(lengths), 1),
        "fn_len_max": max(lengths),
        "params_max": max(params),
        "over_threshold": len(complex_fns),
        "complex_functions": sorted(complex_fns, key=lambda c: -c["ccn"])[:15],
    }


def comment_stats(files: list[str]) -> dict:
    """Line-based code/comment/blank split across languages. Heuristic: it tracks
    block comments (including ones opened after code on the same line) but does not
    parse strings, which is fine for a ratio tripwire — the alarm is a ratio near 0
    or absurdly high, not a precise count."""
    code = comment = blank = 0
    for f in files:
        in_block = False
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for raw in lines:
            s = raw.strip()
            if in_block:
                comment += 1
                if "*/" in s:
                    in_block = False
                continue
            if not s:
                blank += 1
            elif s.startswith("#") or s.startswith("//"):
                comment += 1
            elif "/*" in s:
                # `/*` may follow code on the line; classify by what comes first.
                comment += 1 if s.startswith("/*") else 0
                code += 0 if s.startswith("/*") else 1
                in_block = "*/" not in s.split("/*", 1)[1]
            else:
                code += 1
    total = code + comment
    return {"code_lines": code, "comment_lines": comment, "blank_lines": blank,
            "comment_ratio": round(comment / total, 3) if total else 0.0}


def radon_mi(files: list[str]) -> dict | None:
    py = [f for f in files if f.endswith(".py")]
    if not py or not have("radon"):
        return None
    scores: list[float] = []
    for chunk in batches(py, ARG_BATCH):
        rc, out = run(["radon", "mi", "-j", *chunk])
        if rc != 0 or not out.strip():
            continue
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            continue
        scores.extend(v["mi"] for v in data.values() if isinstance(v, dict) and "mi" in v)
    return {"mi_avg": round(sum(scores) / len(scores), 1), "files": len(scores)} if scores else None


def jscpd_dup(paths: list[str]) -> dict | None:
    if not have("jscpd"):
        return None
    # A fresh per-call dir means "no report" unambiguously signals failure — no
    # risk of reading a stale report (notably in --compare, where both arms run).
    out_dir = tempfile.mkdtemp(prefix="gc_jscpd_")
    try:
        run(["npx", "--yes", "jscpd@latest", *paths, "--silent",
             "--reporters", "json", "--output", out_dir], timeout=180)
        report = os.path.join(out_dir, "jscpd-report.json")
        if not os.path.exists(report):
            return None
        with open(report) as fh:
            stats = json.load(fh)["statistics"]["total"]
        return {"dup_pct_lines": round(stats.get("percentage", 0.0), 2), "clones": stats.get("clones", 0)}
    except (OSError, KeyError, json.JSONDecodeError):
        return None
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def scan_smells(files: list[str]) -> list[dict]:
    hits = []
    for f in files:
        lang = lang_of(f)
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for rule, langs, pat in SMELLS:
            if lang not in langs:
                continue
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                snippet = text[m.start():m.start() + 80].splitlines()[0]
                hits.append({"rule": rule, "file": f, "line": line, "code": snippet})
    return hits


def measure(paths: list[str], do_dup: bool = True) -> dict:
    files = sorted({f for p in paths for f in discover(p)})
    if not files:
        return {"error": "no Python/TypeScript/Go files found", "paths": paths}
    by_lang: dict[str, int] = {}
    has_py = False
    for f in files:
        lang = lang_of(f)
        by_lang[lang] = by_lang.get(lang, 0) + 1
        has_py = has_py or lang == "python"

    result = {
        "files": len(files), "by_language": by_lang,
        "size_complexity": lizard_metrics(files),
        "comments": comment_stats(files),
        "maintainability": radon_mi(files),
        "duplication": jscpd_dup(paths) if do_dup else None,
        "smells": scan_smells(files),
    }
    # Report a backend as missing only when it is genuinely not installed (via
    # `have`), distinct from "ran but found nothing" — so the hint isn't misleading.
    needed = [("lizard", True), ("radon", has_py), ("jscpd", do_dup)]
    result["missing_backends"] = [name for name, required in needed if required and not have(name)]
    return result


def fmt_block(label: str, m: dict) -> str:
    if m.get("error"):
        return f"== {label} ==\n{m['error']}"
    lines = [f"== {label} ==", f"files: {m.get('files')}  languages: {m.get('by_language')}"]
    sc = m.get("size_complexity") or {}
    if sc.get("functions"):
        lines.append(f"complexity: {sc['functions']} fns | CCN avg {sc['ccn_avg']} max {sc['ccn_max']} "
                     f"| len avg {sc['fn_len_avg']} max {sc['fn_len_max']} | {sc['over_threshold']} over threshold")
    c = m.get("comments", {})
    lines.append(f"comments: ratio {c.get('comment_ratio')} ({c.get('comment_lines')} comment / {c.get('code_lines')} code)")
    if m.get("maintainability"):
        lines.append(f"maintainability index (py): {m['maintainability']['mi_avg']}")
    if m.get("duplication"):
        lines.append(f"duplication: {m['duplication']['dup_pct_lines']}% ({m['duplication']['clones']} clones)")
    if m.get("smells"):
        by_rule: dict[str, int] = {}
        for s in m["smells"]:
            by_rule[s["rule"]] = by_rule.get(s["rule"], 0) + 1
        lines.append(f"smell hits: {by_rule}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--compare", nargs=2, metavar=("BASE", "CAND"))
    ap.add_argument("--no-dup", action="store_true")
    args = ap.parse_args()

    if args.compare:
        base, cand = (measure([p], do_dup=not args.no_dup) for p in args.compare)
        if args.json:
            print(json.dumps({"baseline": base, "candidate": cand}, indent=2))
            return 0
        print(fmt_block("BASELINE " + args.compare[0], base))
        print()
        print(fmt_block("CANDIDATE " + args.compare[1], cand))
        return 0

    if not args.paths:
        ap.print_help()
        return 2
    m = measure(args.paths, do_dup=not args.no_dup)
    if args.json:
        print(json.dumps(m, indent=2))
        return 0
    print(fmt_block(" + ".join(args.paths), m))
    if m.get("missing_backends"):
        print("\nmissing tools (using fallbacks):", ", ".join(m["missing_backends"]))
        print("install:  uv tool install lizard radon   |   duplication needs node/npx (jscpd)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
