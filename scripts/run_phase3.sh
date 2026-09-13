#!/bin/sh
# POSIX twin of run_phase3.ps1 (authoritative: .ps1 on the pinned host).
# Mechanical PC contract compilation: source check, compile, derive,
# independent rederive, byte-compare, label audit, tests, seal.
# Usage: sh run_phase3.sh <repo-root> [python-exe]
set -eu
# [P3-LOG-010] Step: start Phase 3, resolve arguments.
echo "[P3:phase3:010] start Phase 3 mechanical contract compilation"
REPO_ROOT="$1"; PYTHON_EXE="${2:-python3}"
echo "[P3:phase3:012] repo=$REPO_ROOT"
# [P3-LOG-020] Step: source check.
echo "[P3:phase3:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
# [P3-LOG-025] Step: models self-check.
echo "[P3:phase3:025] checking PC data models"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/models.py" --self-check
# [P3-LOG-030] Step: compile the primary contract.
echo "[P3:phase3:030] compiling primary contract"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/compile_contract.py" "$REPO_ROOT" "$REPO_ROOT/artifacts/contracts/pc_xacml_primary.contract.json"
# [P3-LOG-040] Step: derive touch (primary).
echo "[P3:phase3:040] deriving touch (primary)"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/derive_touch.py" "$REPO_ROOT/artifacts/contracts/pc_xacml_primary.contract.json" "$REPO_ROOT/artifacts/contracts/touch.json"
# [P3-LOG-050] Step: rederive touch (independent) and byte-compare.
echo "[P3:phase3:050] rederiving touch (independent)"
TMP_TOUCH="${TMPDIR:-/tmp}/pc-xacml-touch-indep.json"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/independent_touch.py" "$REPO_ROOT/artifacts/contracts/pc_xacml_primary.contract.json" "$TMP_TOUCH"
echo "[P3:phase3:052] comparing touch bytes"
"$PYTHON_EXE" -c "import sys; a=open(sys.argv[1],'rb').read(); b=open(sys.argv[2],'rb').read(); sys.exit(0 if a==b else 1)" "$REPO_ROOT/artifacts/contracts/touch.json" "$TMP_TOUCH"
echo "[P3:phase3:054] dual touch agreement ok"
# [P3-LOG-060] Step: no-manual-label audit.
echo "[P3:phase3:060] auditing no-manual-labels"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/check_no_manual_labels.py" "$REPO_ROOT"
# [P3-LOG-070] Step: run the Phase-3 tests.
echo "[P3:phase3:070] running Phase-3 tests"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_touch_derivation.py tests/test_no_manual_touch_labels.py -s)
# [P3-LOG-080] Step: seal the Phase-3 manifest.
echo "[P3:phase3:080] sealing Phase-3 manifest"
PC_REPO_ROOT="$REPO_ROOT" "$PYTHON_EXE" -c "import hashlib,json,os; r=os.environ['PC_REPO_ROOT']; files=['artifacts/contracts/pc_xacml_primary.contract.json','artifacts/contracts/touch.json','derived/anchor_ledger.json','external/MANIFEST.json','prereg/execution_inputs.json']; d={f:hashlib.sha256(open(os.path.join(r,f),'rb').read()).hexdigest() for f in files}; m={'phase':3,'contract_sha256':d['artifacts/contracts/pc_xacml_primary.contract.json'],'touch_sha256':d['artifacts/contracts/touch.json'],'anchor_ledger_sha256':d['derived/anchor_ledger.json'],'external_manifest_sha256':d['external/MANIFEST.json'],'execution_inputs_sha256':d['prereg/execution_inputs.json'],'files':d,'derivation':{'compiler':'src/pc/compile_contract.py','primary':'src/pc/derive_touch.py','independent':'src/audit/independent_touch.py'}}; json.dump(m,open(os.path.join(r,'artifacts/seal/phase3_manifest.json'),'w'),indent=2,sort_keys=True)"
echo "[P3:phase3:082] manifest sealed"
# [P3-LOG-090] Step: gate summary.
echo "[P3:phase3:090] Phase-3 gate: contract, S0 open, successors closed, touch mechanical, dual agreement, no manual labels, hashes sealed"
# [P3-LOG-100] Step: complete.
echo "[P3:phase3:100] Phase 3 complete"
