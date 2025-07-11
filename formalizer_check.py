#!/usr/bin/env python
"""
formalizer_check.py – end-to-end LL​M-as-Formalizer test without temp files.

Usage
-----
python formalizer_check.py \
    data/textual_blocksworld/BlocksWorld-100_PDDL/domain.pddl \
    data/textual_blocksworld/BlocksWorld-100_PDDL/p01.pddl
"""
from __future__ import annotations

import argparse, os, signal, subprocess, sys, textwrap
import shutil
from pathlib import Path
from typing import Tuple

TIME_LIMIT = 5        # seconds


# ───────────────────────────────────────────────────────────────────────────── #
# helpers                                                                      #
# ───────────────────────────────────────────────────────────────────────────── #
def _kill_proc_tree(pid: int, sig=signal.SIGTERM) -> None:
    """Kill a process group given Popen.pid (SIGTERM by default)."""
    try:
        os.killpg(pid, sig)
    except ProcessLookupError:
        pass


# ───────────────────────────────────────────────────────────────────────────── #
# solver                                                                       #
# ───────────────────────────────────────────────────────────────────────────── #
def run_solver(domain: str, problem: str, time_limit: int = TIME_LIMIT) -> Tuple[str | None, str]:
    """Run dual-bfws-ffparser offline and return (plan_text | None, log_text)."""
    if shutil.which("planutils") is None:
        raise FileNotFoundError("'planutils' command not found; please install planutils")

    plan_path = Path.cwd() / "plan"
    plan_path.unlink(missing_ok=True)

    cmd = ["planutils", "run", "dual-bfws-ffparser", domain, problem]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,   # separate process group
    )

    try:
        stdout, stderr = proc.communicate(timeout=time_limit)
    except subprocess.TimeoutExpired:
        _kill_proc_tree(proc.pid, signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            _kill_proc_tree(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()

    log_text = (stderr or "") + (stdout or "")

    # echo to console
    print(textwrap.dedent("""\
        ── SOLVER LOG ────────────────────────────────────────────────
        {log}
        ──────────────────────────────────────────────────────────────
    """).format(log=log_text.rstrip()))

    plan_text: str | None = None
    if plan_path.exists() and plan_path.stat().st_size:
        plan_text = plan_path.read_text(encoding="utf-8")
    plan_path.unlink(missing_ok=True)

    return plan_text, log_text


# ───────────────────────────────────────────────────────────────────────────── #
# validator                                                                    #
# ───────────────────────────────────────────────────────────────────────────── #
def run_val(domain: str, problem: str, plan_file: str) -> Tuple[bool, str]:
    """Return (is_valid, log_text)."""
    cmd = ["planutils", "run", "val", "Validate", domain, problem, plan_file]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log_text = (proc.stdout or "") + (proc.stderr or "")

    print(textwrap.dedent("""\
        ── VAL LOG ───────────────────────────────────────────────────
        {log}
        ──────────────────────────────────────────────────────────────
    """).format(log=log_text.rstrip()))

    return "Plan valid" in log_text, log_text


# ───────────────────────────────────────────────────────────────────────────── #
# main                                                                         #
# ───────────────────────────────────────────────────────────────────────────── #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("domain")
    ap.add_argument("problem")
    ns = ap.parse_args()

    # 1) solve
    try:
        plan_txt, solver_log = run_solver(ns.domain, ns.problem)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)
    if plan_txt is None:
        print("❌  Solver failed or timed-out.")
        sys.exit(1)

    # write plan to a throw-away file for VAL
    tmp_plan = Path("plan_tmp.txt")
    tmp_plan.write_text(plan_txt, encoding="utf-8")

    # 2) validate
    is_ok, val_log = run_val(ns.domain, ns.problem, str(tmp_plan))
    tmp_plan.unlink(missing_ok=True)

    if is_ok:
        print("🎉  Plan is VALID.")
    else:
        print("⚠️  Plan INVALID.")
        sys.exit(2)


if __name__ == "__main__":
    main()
