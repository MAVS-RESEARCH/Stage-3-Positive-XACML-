#!/bin/sh
# POSIX twin of run_phase1.ps1 (authoritative: .ps1 on the pinned host).
# Same ordered steps; each echoes a [P1:phase1:NNN] console line.
# Usage: sh run_phase1.sh <repo-root> <spec-source> <maven-cmd> [python-exe]
set -eu
# [P1-LOG-010] Step: start Phase 1, resolve arguments.
echo "[P1:phase1:010] start Phase 1 external source lock and native reproduction"
REPO_ROOT="$1"; SPEC_SOURCE="$2"; MAVEN_CMD="$3"; PYTHON_EXE="${4:-python3}"
echo "[P1:phase1:012] repo=$REPO_ROOT"
WORK_DIR="${TMPDIR:-/tmp}/pc-xacml-p1"
mkdir -p "$WORK_DIR"
CLONE_DIR="$REPO_ROOT/external/authzforce-repo"
# [P1-LOG-020] Step: lock external sources.
echo "[P1:phase1:020] locking external sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/lock_sources.py" "$REPO_ROOT" "$CLONE_DIR"
# [P1-LOG-030] Step: seal the authoritative spec.
echo "[P1:phase1:030] sealing authoritative spec"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/seal_spec.py" "$REPO_ROOT" "$SPEC_SOURCE"
# [P1-LOG-040] Step: record environment (scrub-safe fields only).
echo "[P1:phase1:040] recording environment"
mkdir -p "$REPO_ROOT/artifacts/raw"
{ echo "experiment_id=PC-XACML-S3PLUS-v1"; echo "phase=1"; uname -a; "$PYTHON_EXE" --version; java -version 2>&1 | head -1; git --version; "$MAVEN_CMD" -version 2>&1 | head -1; } > "$REPO_ROOT/artifacts/raw/environment.txt"
echo "[P1:phase1:042] environment recorded"
# [P1-LOG-050] Step: build pinned PDP modules.
echo "[P1:phase1:050] building pinned AuthzForce PDP modules"
(cd "$CLONE_DIR" && "$MAVEN_CMD" -pl pdp-testutils -am -DskipTests "-Dgpg.skip=true" package)
# [P1-LOG-060] Step: classpath + driver compile.
echo "[P1:phase1:060] assembling PDP backend"
(cd "$CLONE_DIR" && "$MAVEN_CMD" -pl pdp-testutils "-DincludeScope=test" "-Dmdep.outputFile=$WORK_DIR/pdp-cp.txt" dependency:build-classpath)
CP_FILE="$WORK_DIR/pdp-cp.txt"
TEST_CLASSES="$CLONE_DIR/pdp-testutils/target/test-classes"
PDP_CLASSES="$CLONE_DIR/pdp-testutils/target/classes"
DRIVER_CLASSES="$WORK_DIR/driver-classes"
mkdir -p "$DRIVER_CLASSES"
DEPS_CP=$(cat "$CP_FILE")
echo "[P1:phase1:062] compiling PdpRunner driver"
javac -cp "$TEST_CLASSES:$PDP_CLASSES:$DEPS_CP" -d "$DRIVER_CLASSES" "$REPO_ROOT/src/xacml/PdpRunner.java"
echo "[P1:phase1:064] backend ready"
# [P1-LOG-070] Step: construct (not execute) completed requests.
echo "[P1:phase1:070] constructing completed requests"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/build_repaired_requests.py" "$REPO_ROOT/external/authzforce/fixture/request.xml" "$REPO_ROOT/external/authzforce/fixture/response.xml" "$REPO_ROOT/external/authzforce/fixture/policies/policy.xml" "riddle me this" "not-riddle-me-this" "$REPO_ROOT/derived/requests"
# [P1-LOG-080] Step: original-only native execution.
echo "[P1:phase1:080] executing original fixture on frozen PDP"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/run_authzforce.py" --mode original --phase1-only-original --repo-root "$REPO_ROOT" --java java --cp-file "$CP_FILE" --pdp-test-classes "$TEST_CLASSES" --pdp-classes "$PDP_CLASSES" --driver-classes "$DRIVER_CLASSES" --work-dir "$WORK_DIR/run" --out "$REPO_ROOT/artifacts/raw/original_response_actual.xml"
# [P1-LOG-090] Step: stage expected + compare.
echo "[P1:phase1:090] comparing actual vs expected response"
cp "$REPO_ROOT/external/authzforce/fixture/response.xml" "$REPO_ROOT/artifacts/raw/original_response_expected.xml"
echo "[P1:phase1:092] semantic comparison"
"$PYTHON_EXE" "$REPO_ROOT/src/xacml/parse_response.py" "$REPO_ROOT/artifacts/raw/original_response_actual.xml" "$REPO_ROOT/artifacts/raw/original_response_expected.xml" "$REPO_ROOT/artifacts/raw/original_response_comparison.json"
# [P1-LOG-100] Step: tests.
echo "[P1:phase1:100] running Phase-1 tests"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/test_source_hashes.py tests/test_original_fixture.py tests/test_phase1_no_completed_execution.py tests/test_prereg_seal.py -s)
# [P1-LOG-110] Step: gate summary.
echo "[P1:phase1:110] Phase-1 gate summary: see test results above"
# [P1-LOG-120] Step: complete.
echo "[P1:phase1:120] Phase 1 complete"
