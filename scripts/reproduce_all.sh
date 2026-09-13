#!/bin/sh
# POSIX twin of reproduce_all.ps1 (authoritative: .ps1 on the pinned host).
# Replays every phase in verify-only modes from a checkout: sealed human/
# model judgments are verified by hash, never regenerated. Fails fast.
# Usage: sh reproduce_all.sh <repo-root> [python-exe]
set -eu
# [P6-LOG-R10] Step: start reproduction replay, resolve arguments.
echo "[P6:repro:010] start reproduction replay"
REPO_ROOT="$1"; PYTHON_EXE="${2:-python3}"
# [P6-LOG-R12] Step: echo the resolved repository root.
echo "[P6:repro:012] repo=$REPO_ROOT"
# [P6-LOG-R20] Step: sealed sources (no re-lock, verify only).
echo "[P6:repro:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
# [P6-LOG-R30] Step: sealed packet and launch records (hash verify only).
echo "[P6:repro:030] verifying sealed packet and launch records"
"$PYTHON_EXE" "$REPO_ROOT/scripts/repro_compare.py" packet-verify "$REPO_ROOT"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/launch_freeze.py" --repo-root "$REPO_ROOT" --status
# [P6-LOG-R40] Step: deterministic derivations re-checked via test suites.
echo "[P6:repro:040] running derivation test suites"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_touch_derivation.py tests/test_no_manual_touch_labels.py tests/test_all_freezes.py tests/test_completion_space.py -q)
# [P6-LOG-R50] Step: seal and manifest presence (hash verify only).
echo "[P6:repro:050] verifying seal and manifest"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/build_audit_report.py" "$REPO_ROOT"
test -f "$REPO_ROOT/artifacts/seal/FINAL_RESULT_LAUNCH.json"
test -f "$REPO_ROOT/MANIFEST.sha256"
# [P6-LOG-R60] Step: reproduction replay complete.
echo "[P6:repro:060] reproduction replay complete"
