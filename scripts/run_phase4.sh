#!/bin/sh
# POSIX twin of run_phase4.ps1 (authoritative: .ps1 on the pinned host).
# Exact all-freeze evaluation: source check, primary + independent solves,
# agreement assert, completion-space certificate + singleton gate.
# Sealed-output comparison lives in tests only; this script never opens
# sealed output files.
# Usage: sh run_phase4.sh <repo-root> [python-exe]
set -eu
# [P4-LOG-010] Step: start Phase 4, resolve arguments.
echo "[P4:phase4:010] start Phase 4 exact all-freeze evaluation"
REPO_ROOT="$1"; PYTHON_EXE="${2:-python3}"
# [P4-LOG-012] Step: echo the resolved repository root.
echo "[P4:phase4:012] repo=$REPO_ROOT"
CONTRACT="$REPO_ROOT/artifacts/contracts/pc_xacml_primary.contract.json"
TOUCH="$REPO_ROOT/artifacts/contracts/touch.json"
EXEC_INPUTS="$REPO_ROOT/prereg/execution_inputs.json"
FREEZES="$REPO_ROOT/artifacts/freezes"
SEAL="$REPO_ROOT/artifacts/seal"
INDEP_TMP="${TMPDIR:-/tmp}/pc-xacml-phase4-indep"
# [P4-LOG-020] Step: source check.
echo "[P4:phase4:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
# [P4-LOG-030] Step: primary exhaustive solve.
echo "[P4:phase4:030] running primary solver"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/solve_freezes.py" "$CONTRACT" "$TOUCH" "$EXEC_INPUTS" "$FREEZES"
# [P4-LOG-040] Step: independent exhaustive solve.
echo "[P4:phase4:040] running independent solver"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/independent_solver.py" "$CONTRACT" "$TOUCH" "$EXEC_INPUTS" "$INDEP_TMP"
# [P4-LOG-050] Step: assert dual-solver agreement.
echo "[P4:phase4:050] asserting dual-solver agreement"
"$PYTHON_EXE" - "$FREEZES" "$INDEP_TMP" <<'PY'
import json, os, sys
prim, indep = sys.argv[1], sys.argv[2]
with open(os.path.join(prim, "K_table.json"), encoding="utf-8") as h:
    p = json.load(h)
with open(os.path.join(indep, "K_table.json"), encoding="utf-8") as h:
    q = json.load(h)
assert p["kappa"] == q["kappa"], (p["kappa"], q["kappa"])
assert p["freeze_order"] == q["freeze_order"]
assert p["contract_sha256"] == q["contract_sha256"]
for name in p["freeze_order"]:
    with open(os.path.join(prim, name + ".json"), encoding="utf-8") as h:
        pr = json.load(h)
    with open(os.path.join(indep, name + ".json"), encoding="utf-8") as h:
        ir = json.load(h)
    assert pr["removed_actions"] == ir["removed_actions"], name
    assert pr["surviving_actions"] == ir["surviving_actions"], name
    assert pr["proper_closer_exists"] == ir["proper_closer_exists"], name
    assert pr["kappa"] == ir["kappa"], name
print("[P4:phase4:052] dual agreement holds")
PY
# [P4-LOG-060] Step: completion-space certificate + singleton gate.
echo "[P4:phase4:060] checking completion space"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/check_completion_space.py" "$REPO_ROOT" "$CONTRACT" "$FREEZES/K_table.json" "$SEAL/completion_space_certificate.json" "$FREEZES/identified_set.json"
# [P4-LOG-070] Step: Phase-4 tests.
echo "[P4:phase4:070] running Phase-4 tests"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_all_freezes.py tests/test_completion_space.py -s)
# [P4-LOG-080] Step: gate summary.
echo "[P4:phase4:080] Phase-4 gate summary: see test results above"
# [P4-LOG-090] Step: complete.
echo "[P4:phase4:090] Phase 4 complete"
