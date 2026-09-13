#!/bin/sh
# POSIX twin of run_phase5.ps1 (authoritative: .ps1 on the pinned host).
# Falsification, sensitivity, anti-circularity audit: source check,
# sealed-presence check (hash only), raw execution via frozen PDP,
# post-execution comparison, perturbations, cost/negative sweeps,
# ablations, label injection, leakage, clean repro, tests.
# Frozen external/ never mutated; all variants in temp copies.
# Usage: sh run_phase5.sh <repo-root> [python-exe] [java-home] [work-dir]
set -eu
# [P5-LOG-010] Step: start Phase 5, resolve arguments.
echo "[P5:phase5:010] start Phase 5 falsification, sensitivity, anti-circularity audit"
REPO_ROOT="$1"; PYTHON_EXE="${2:-python3}"; JAVA_HOME="${3:-/usr/lib/jvm/default}"; WORK_DIR="${4:-${TMPDIR:-/tmp}/pc-xacml-p1}"
echo "[P5:phase5:012] repo=$REPO_ROOT"
AUDITS="$REPO_ROOT/artifacts/audits"
JAVA_EXE="$JAVA_HOME/bin/java"
CP_FILE="$WORK_DIR/pdp-cp.txt"
AUTHZ_REPO="$REPO_ROOT/external/authzforce-repo"
TEST_CLASSES="$AUTHZ_REPO/pdp-testutils/target/test-classes"
PDP_CLASSES="$AUTHZ_REPO/pdp-testutils/target/classes"
DRIVER_CLASSES="$WORK_DIR/driver-classes"
mkdir -p "$AUDITS"
# [P5-LOG-020] Step: source check.
echo "[P5:phase5:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
# [P5-LOG-022] Step: sealed-presence check (hash only, never opened).
echo "[P5:phase5:022] checking sealed canary expectations exist (hash only)"
if ! grep -q "canary_expectations.json" "$REPO_ROOT/prereg/prereg_sha256.txt"; then echo "sealed hash missing" >&2; exit 1; fi
if [ ! -f "$REPO_ROOT/prereg/canary_expectations.json" ]; then echo "sealed file missing" >&2; exit 1; fi
# [P5-LOG-024] Step: presence confirmed without opening sealed values.
echo "[P5:phase5:024] sealed expectations present (not opened during execution)"
# [P5-LOG-030] Step: backend check.
echo "[P5:phase5:030] checking frozen PDP backend"
if [ ! -f "$CP_FILE" ] || [ ! -f "$DRIVER_CLASSES/PdpRunner.class" ]; then echo "backend absent" >&2; exit 1; fi
echo "[P5:phase5:032] backend present"
# [P5-LOG-040] Step: 5.1 corruption.
echo "[P5:phase5:040] running hash-corruption control (5.1)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" corruption
# [P5-LOG-050] Step: raw canary execution.
echo "[P5:phase5:050] running canary raw execution (5.2-5.5, 5.9)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" canary_raw "$JAVA_EXE" "$CP_FILE" "$TEST_CLASSES" "$PDP_CLASSES" "$DRIVER_CLASSES"
# [P5-LOG-052] Step: post-execution comparison.
echo "[P5:phase5:052] comparing canary raws vs sealed expectations"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/compare_canary_outcomes.py" "$REPO_ROOT" "$AUDITS"
# [P5-LOG-060] Step: perturbations + interface change.
echo "[P5:phase5:060] running preserving perturbations (5.6) + interface change (5.7)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" perturbation "$JAVA_EXE" "$CP_FILE" "$TEST_CLASSES" "$PDP_CLASSES" "$DRIVER_CLASSES"
# [P5-LOG-070] Step: cost sweep.
echo "[P5:phase5:070] running cost sweep (5.8)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" cost
# [P5-LOG-080] Step: negative-world sweep.
echo "[P5:phase5:080] running negative-world sweep (5.9)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" negative
# [P5-LOG-090] Step: ablations.
echo "[P5:phase5:090] running anchor ablations (5.10)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" ablation
# [P5-LOG-100] Step: label injection.
echo "[P5:phase5:100] running label-injection control (5.11)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" label
# [P5-LOG-110] Step: leakage audit.
echo "[P5:phase5:110] running leakage audit (5.12)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" leakage
# [P5-LOG-120] Step: clean reproduction.
echo "[P5:phase5:120] running clean reproduction (5.13)"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/phase5_execute.py" "$REPO_ROOT" "$AUDITS" cleanrepro "$JAVA_EXE" "$CP_FILE" "$TEST_CLASSES" "$PDP_CLASSES" "$DRIVER_CLASSES"
# [P5-LOG-130] Step: Phase-5 tests.
echo "[P5:phase5:130] running Phase-5 tests"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_parser_corruptions.py tests/test_cost_robustness.py tests/test_interface_preserving_mutations.py tests/test_anchor_ablation.py tests/test_clean_reproduction.py -s)
# [P5-LOG-140] Step: gate summary.
echo "[P5:phase5:140] Phase-5 gate summary: see test results above"
# [P5-LOG-150] Step: complete.
echo "[P5:phase5:150] Phase 5 complete"
