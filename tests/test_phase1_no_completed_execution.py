"""Phase-1 ordering test: no completed-world execution in Phase 1.

Scopes strictly to the current checkout's outputs/logs (never the sealed
primary commit): asserts no completed-world PDP output artifact exists
under artifacts/, no completed-mode invocation appears in run logs, and
the execution wrapper refuses completed mode under
--phase1-only-original with exit code 2.
"""
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "xacml"))

import run_authzforce  # noqa: E402


def test_no_completed_world_outputs():
    """No x_permit/x_nonpermit PDP outputs exist in this checkout."""
    # [P1-LOG-T30] Test step: scan current-checkout artifacts only.
    print("[P1:test:ordering:030] scanning artifacts for completed outputs",
          flush=True)
    hits = []
    artifacts = os.path.join(REPO_ROOT, "artifacts")
    for base, _dirs, files in os.walk(artifacts):
        for name in files:
            lowered = name.lower()
            if "x_permit" in lowered or "x_nonpermit" in lowered:
                hits.append(os.path.join(base, name))
    assert hits == [], hits


def test_no_completed_mode_in_logs():
    """No completed-mode PDP invocation appears in run logs."""
    # [P1-LOG-T32] Test step: scan current-checkout logs only.
    print("[P1:test:ordering:032] scanning logs for completed invocations",
          flush=True)
    logs_dir = os.path.join(REPO_ROOT, "artifacts", "logs")
    if not os.path.isdir(logs_dir):
        return
    for name in sorted(os.listdir(logs_dir)):
        path = os.path.join(logs_dir, name)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as handle:
            content = handle.read()
        assert "mode=completed" not in content, name


def test_completed_mode_refused():
    """--phase1-only-original refuses completed mode with exit code 2."""
    # [P1-LOG-T34] Test step: assert the ordering refusal path.
    print("[P1:test:ordering:034] asserting completed-mode refusal",
          flush=True)
    try:
        run_authzforce.main([
            "--mode", "completed", "--world", "x_permit",
            "--request", "request_x_permit.xml",
            "--phase1-only-original", "--repo-root", REPO_ROOT,
            "--java", "java", "--cp-file", "cp.txt",
            "--pdp-test-classes", "t", "--pdp-classes", "c",
            "--driver-classes", "d", "--work-dir", "w",
            "--out", "o.xml"])
    except SystemExit as exc:
        assert exc.code == 2, exc.code
    else:
        raise AssertionError("completed mode was not refused")
