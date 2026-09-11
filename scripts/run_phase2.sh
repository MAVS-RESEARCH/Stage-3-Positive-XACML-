#!/bin/sh
# POSIX twin of run_phase2.ps1 (authoritative: .ps1 on the pinned host).
# Modes: primary (2A, packet, gated target audit), reproduce (verify only),
# readjudicate (rebuild packet). Each echoes a [P2:phase2:NNN] console line.
# Usage: sh run_phase2.sh <mode> <repo-root> <maven-cmd> [python-exe]
set -eu
# [P2-LOG-010] Step: start Phase 2, resolve arguments.
echo "[P2:phase2:010] start Phase 2 semantic anchor audit"
MODE="$1"; REPO_ROOT="$2"; MAVEN_CMD="$3"; PYTHON_EXE="${4:-python3}"
echo "[P2:phase2:012] mode=$MODE repo=$REPO_ROOT"
WORK_DIR="${TMPDIR:-/tmp}/pc-xacml-p1"
DERIVED="$REPO_ROOT/derived"
FIXTURE="$REPO_ROOT/external/authzforce/fixture"
MANIFEST="$REPO_ROOT/external/MANIFEST.json"
EXEC_INPUTS="$REPO_ROOT/prereg/execution_inputs.json"
# [P2-LOG-020] Step: source check.
echo "[P2:phase2:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
if [ "$MODE" = "readjudicate" ]; then
  # [P2-LOG-025] Step: rebuild the packet for fresh adjudication.
  echo "[P2:phase2:025] rebuilding blind packet for readjudication"
  "$PYTHON_EXE" "$REPO_ROOT/src/audit/blind_adjudication.py" --repo-root "$REPO_ROOT" --build-packet
  echo "[P2:phase2:120] readjudication packet ready"
  exit 0
fi
# [P2-LOG-040] Step: 2A projection + adequacy.
echo "[P2:phase2:040] projecting frozen policy"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/parse_policy.py" "$FIXTURE/policies/policy.xml" "$MANIFEST" "$DERIVED/policy_projection.json"
echo "[P2:phase2:042] certifying projection adequacy"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/check_policy_adequacy.py" "$DERIVED/policy_projection.json" "$FIXTURE/pdp.xml" "$MANIFEST" "$DERIVED/policy_adequacy_certificate.json"
# [P2-LOG-050] Step: route-(a) probe + route-(b) proof.
echo "[P2:phase2:050] probing route-(a) availability"
CLONE_DIR="$REPO_ROOT/external/authzforce-repo"
CP_FILE="$WORK_DIR/pdp-cp.txt"
PDP_CLASSES="$CLONE_DIR/pdp-testutils/target/classes"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/capture_resolved_context.py" "$REPO_ROOT" "$JAVA_HOME" "$PDP_CLASSES" "$CP_FILE" "$DERIVED/route_a_probe.json"
echo "[P2:phase2:052] proving H-equivalence (route b)"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/prove_h_equivalence.py" "$FIXTURE/request.xml" "$DERIVED/requests/request_x_permit.xml" "$DERIVED/requests/request_x_nonpermit.xml" "$DERIVED/policy_projection.json" "$DERIVED/policy_adequacy_certificate.json" "$DERIVED/route_a_probe.json" "$FIXTURE/pdp.xml" "$DERIVED/h_equivalence_proof.json"
# [P2-LOG-060] Step: derive H / P_R / Lambda / Atom records.
echo "[P2:phase2:060] deriving H objects"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/derive_H.py" "$FIXTURE/request.xml" "$DERIVED/requests/request_x_permit.xml" "$DERIVED/requests/request_x_nonpermit.xml" "$DERIVED/h_equivalence_proof.json" "$DERIVED" "$REPO_ROOT/artifacts/audits/H_provenance.json"
echo "[P2:phase2:062] deriving P_R relation"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/derive_PR.py" "$DERIVED/policy_projection.json" "$DERIVED/policy_adequacy_certificate.json" "$DERIVED/pr_relation.json"
echo "[P2:phase2:064] recording Lambda"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/derive_Lambda.py" "$FIXTURE/pdp.xml" "$FIXTURE/policies/policy.xml" "$MANIFEST" "$DERIVED/lambda_record.json"
echo "[P2:phase2:066] proving Atom record"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/derive_atom.py" "$FIXTURE/request.xml" "$DERIVED/requests/request_x_permit.xml" "$DERIVED/requests/request_x_nonpermit.xml" "$REPO_ROOT/src/xacml/build_repaired_requests.py" "$EXEC_INPUTS" "$DERIVED/atom_record.json"
# [P2-LOG-070] Step: assemble ledger (0/2/4 semantics honoured by caller).
echo "[P2:phase2:070] assembling anchor ledger"
"$PYTHON_EXE" "$REPO_ROOT/src/pc/check_anchor_completeness.py" "$REPO_ROOT" "$DERIVED"
# [P2-LOG-080] Step: build + seal the blind auditor packet.
echo "[P2:phase2:080] building blind auditor packet"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/blind_adjudication.py" --repo-root "$REPO_ROOT" --build-packet
if [ "$MODE" = "reproduce" ]; then
  # [P2-LOG-085] Step: reproduce mode verifies only.
  echo "[P2:phase2:085] reproduce mode: verification only"
  echo "[P2:phase2:120] Phase 2 reproduce complete"
  exit 0
fi
# [P2-LOG-090] Step: judge unlock before any completed-world execution.
echo "[P2:phase2:090] judging target-audit unlock"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/blind_adjudication.py" --repo-root "$REPO_ROOT" --assert-unlock
# [P2-LOG-100] Step: unlocked target audit only (first completed execution).
echo "[P2:phase2:100] unlock holds: running target audit"
TEST_CLASSES="$CLONE_DIR/pdp-testutils/target/test-classes"
DRIVER_CLASSES="$WORK_DIR/driver-classes"
for WORLD in x_permit x_nonpermit; do
  "$PYTHON_EXE" "$REPO_ROOT/src/xacml/run_authzforce.py" --mode completed --world "$WORLD" --request "$DERIVED/requests/request_$WORLD.xml" --repo-root "$REPO_ROOT" --java java --cp-file "$CP_FILE" --pdp-test-classes "$TEST_CLASSES" --pdp-classes "$PDP_CLASSES" --driver-classes "$DRIVER_CLASSES" --work-dir "$WORK_DIR/target" --out "$REPO_ROOT/artifacts/raw/target_${WORLD}_actual.xml"
done
# [P2-LOG-110] Step: Phase-2 tests.
echo "[P2:phase2:110] running Phase-2 tests"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_policy_projection.py tests/test_policy_adequacy.py tests/test_h_equivalence.py tests/test_anchor_completeness.py tests/test_blind_adjudication.py tests/test_completed_world_decisions.py -s)
# [P2-LOG-120] Step: complete.
echo "[P2:phase2:120] Phase 2 complete"
