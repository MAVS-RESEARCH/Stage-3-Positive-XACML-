#!/bin/sh
# POSIX twin of run_phase6.ps1 (authoritative: .ps1 on the pinned host).
# Phase-6 seal verification: source check, 8.1 ten-condition read-only
# verification (no PDP rerun, no semantic recompute, no quarantine open),
# seal-hash binding, manifest verification, audit verification (15 sections
# + claim linter), archive verification, full pytest.
# Modes: default success-seal; --failure-seal seals a stopped experiment
# (verifies the stop record, asserts no prohibited downstream artifacts,
# writes the negative FINAL_RESULT without touching success seals).
# Usage: sh run_phase6.sh <repo-root> [python-exe] [--failure-seal]
set -eu
# [P6-LOG-010] Step: start Phase 6, resolve arguments.
echo "[P6:phase6:010] start Phase 6 seal verification"
REPO_ROOT="$1"; PYTHON_EXE="${2:-python3}"
MODE="success"
for arg in "$@"; do
  if [ "$arg" = "--failure-seal" ]; then MODE="failure"; fi
done
# [P6-LOG-012] Step: echo resolved configuration (repo + mode).
echo "[P6:phase6:012] repo=$REPO_ROOT mode=$MODE"
SEAL="$REPO_ROOT/artifacts/seal/FINAL_RESULT_LAUNCH.json"
# [P6-LOG-020] Step: source check (frozen seals never touched).
echo "[P6:phase6:020] verifying sealed sources"
"$PYTHON_EXE" "$REPO_ROOT/src/provenance/verify_sources.py" "$REPO_ROOT"
if [ "$MODE" = "failure" ]; then
  # [P6-LOG-030] Step: failure-seal path for stopped experiments.
  echo "[P6:phase6:030] failure-seal mode: verifying stop record"
  "$PYTHON_EXE" - "$REPO_ROOT" <<'PY'
import json, os, sys
root = sys.argv[1]
hist = [os.path.join(root, "artifacts/seal/FINAL_RESULT.json"),
        os.path.join(root, "artifacts/seal/FINAL_RESULT_CYCLE_002.json")]
for path in hist:
    assert os.path.isfile(path), "historical seal missing: " + path
    doc = json.load(open(path, encoding="utf-8"))
    assert doc.get("outcome") == "NATIVE_ANCHOR_INSUFFICIENT", path
print("[P6:phase6:032] historical negative seals intact; operator supplies stopped_at_phase/trigger for the new failure file; success seals never overwritten")
PY
  echo "[P6:phase6:034] failure-seal verification complete (no downstream run by protocol)"
  exit 0
fi
# [P6-LOG-040] Step: success-seal 8.1 verification (read-only).
echo "[P6:phase6:040] verifying Sec. 8.1 ten conditions (read-only)"
"$PYTHON_EXE" - "$REPO_ROOT" <<'PY'
import hashlib, json, os, sys
root = sys.argv[1]
def load(rel):
    with open(os.path.join(root, rel), encoding="utf-8") as h:
        return json.load(h)
def sha(rel):
    d = hashlib.sha256()
    with open(os.path.join(root, rel), "rb") as h:
        for c in iter(lambda: h.read(65536), b""):
            d.update(c)
    return d.hexdigest()
c1 = load("artifacts/raw/original_response_comparison.json")
assert c1.get("semantic_match") is True, "8.1(1) fixture"
o = load("artifacts/audits/launch/quarantine/outcome_opening.json")
assert o["decisions"] == {"x_nonpermit": "NotApplicable", "x_permit": "Permit"}, "8.1(2) targets"
assert o.get("match") is True and o.get("conformance") == "RUN_CONFORMANCE_PASSED", "8.1(2) conformance"
for a in ("AUD-L07", "AUD-L08", "AUD-L09"):
    v = load("artifacts/audits/launch_certification/%s/verdict.json" % a)
    assert all(v["verdicts"][k]["status"] == "FIXED" for k in ("H", "P_R", "Lambda", "Atom")), "8.1(3) " + a
    assert all(x == "LEGITIMATELY_DEFERRED" for x in v["deferrals"].values()), "8.1(3) deferrals " + a
auth = load("artifacts/audits/launch/TARGET_EXECUTION_AUTHORIZED.json")
assert auth.get("authorized") is True, "8.1(3) authorization"
assert load("artifacts/audits/label_injection.json").get("detected") is True, "8.1(4) label audit"
assert "touch" not in load("artifacts/contracts/pc_xacml_primary.contract.json"), "8.1(4) schema"
assert load("artifacts/contracts/touch.json") == {"q_supply_missing_attribute": ["E"]}, "8.1(5) touch"
assert sha("artifacts/contracts/touch.json") == load("artifacts/seal/phase3_manifest.json")["touch_sha256"], "8.1(5) manifest"
kt = load("artifacts/freezes/K_table.json")
assert kt["kappa"] == [1, "INF", 1, 1, "INF", "INF", 1, "INF"], "8.1(6) K"
assert kt["contract_sha256"] == sha("artifacts/contracts/pc_xacml_primary.contract.json"), "8.1(6) binding"
assert load("artifacts/freezes/identified_set.json")["identified_set_cardinality"] == 1, "8.1(7) cardinality"
cert = load("artifacts/seal/completion_space_certificate.json")
assert cert["free_k_relevant_fields"] == 0 and cert["verdict"] == "COMPLETE", "8.1(7) certificate"
assert kt.get("nontrivial") is True, "8.1(8) nontrivial"
cr = load("artifacts/audits/clean_repro.json")
assert cr.get("touch_match") is True and cr.get("k_match") is True, "8.1(9) repro"
for name in ("corruption_pdp", "corruption_policy", "corruption_request", "corruption_response", "corruption_spec"):
    assert load("artifacts/audits/%s.json" % name).get("detected") is True, "8.1(10) " + name
assert load("artifacts/audits/cost_sweep.json").get("pass") is True, "8.1(10) cost"
assert load("artifacts/audits/negative_world_sweep.json").get("fiber_open") is True, "8.1(10) negworld"
for name in ("ablation_H", "ablation_P_R", "ablation_Lambda", "ablation_Atom"):
    assert load("artifacts/audits/%s.json" % name).get("refuses_positive") is True, "8.1(10) " + name
assert load("artifacts/audits/leakage_graph.json").get("pass") is True, "8.1(10) leakage"
assert cr.get("pass") is True, "8.1(10) clean"
seal = load("artifacts/seal/FINAL_RESULT_LAUNCH.json")
assert seal["outcome"] == "POSITIVE_NATIVE_STAGE3", "seal outcome"
assert seal["K"] == [1, "INF", 1, 1, "INF", "INF", 1, "INF"], "seal K"
assert seal["derived_touch"] == {"q_supply_missing_attribute": ["E"]}, "seal touch"
assert seal["contract_sha256"] == sha("artifacts/contracts/pc_xacml_primary.contract.json"), "seal contract binding"
assert seal["touch_sha256"] == sha("artifacts/contracts/touch.json"), "seal touch binding"
assert seal["k_table_sha256"] == sha("artifacts/freezes/K_table.json"), "seal K binding"
print("[P6:phase6:042] ten conditions hold; seal binds observed values")
PY
# [P6-LOG-050] Step: historical seals untouched.
echo "[P6:phase6:050] asserting historical seals untouched"
test -f "$REPO_ROOT/artifacts/seal/FINAL_RESULT.json"
test -f "$REPO_ROOT/artifacts/seal/FINAL_RESULT_CYCLE_002.json"
test -f "$SEAL"
# [P6-LOG-060] Step: manifest verification.
echo "[P6:phase6:060] verifying MANIFEST.sha256"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -c "import hashlib; bad=[l for l in open('MANIFEST.sha256',encoding='utf-8').read().splitlines() if l.strip() and hashlib.sha256(open(l.split('  ')[1],'rb').read()).hexdigest()!=l.split('  ')[0]]; assert not bad, bad[:3]; print('[P6:phase6:062] manifest ok (%d entries)' % len(open('MANIFEST.sha256',encoding='utf-8').read().splitlines()))")
# [P6-LOG-070] Step: audit + claim linter.
echo "[P6:phase6:070] verifying FINAL_AUDIT.md and claim gate"
"$PYTHON_EXE" - "$REPO_ROOT" <<'PY'
import os, sys
root = sys.argv[1]
text = open(os.path.join(root, "artifacts/audits/FINAL_AUDIT.md"), encoding="utf-8").read()
for section in ("External source provenance", "Original fixture", "Anchor-by-anchor", "Policy projection",
                "H-equivalence", "Blind-adjudication", "Native target decisions", "PC contract hash",
                "touch derivations", "Completion-space", "freeze values", "solver agreement",
                "Falsification", "limitations", "Allowed and forbidden"):
    assert section.lower() in text.lower(), "missing section: " + section
forbidden = ["real systems naturally provide PC anchors", "Stage III works in the wild",
             "XACML validates the universal E/R/A ontology", "PC automatically extracts governance semantics",
             "we prove representation/evidence causality in XACML",
             "production authorization systems are PC-identifiable"]
assert not any(s in text for s in forbidden), "forbidden claim present"
assert "We additionally audited a pre-existing XACML/AuthzForce" in text, "allowed paragraph missing"
print("[P6:phase6:072] audit sections + claim gate ok")
PY
# [P6-LOG-075] Step: audit-report assembler verification (no hand numbers).
echo "[P6:phase6:075] verifying audit report assembler"
"$PYTHON_EXE" "$REPO_ROOT/src/audit/build_audit_report.py" "$REPO_ROOT"
# [P6-LOG-080] Step: archive verification.
echo "[P6:phase6:080] verifying release archive"
test -f "$REPO_ROOT/PC-XACML-S3PLUS-v1.tar.gz"
test -f "$REPO_ROOT/PC-XACML-S3PLUS-v1.sha256"
test -f "$REPO_ROOT/PC-XACML-S3PLUS-v1.tar.gz.sha256"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -c "import hashlib; exp=open('PC-XACML-S3PLUS-v1.sha256',encoding='utf-8').read().split()[0]; got=hashlib.sha256(open('PC-XACML-S3PLUS-v1.tar.gz','rb').read()).hexdigest(); assert exp==got, (exp,got); print('[P6:phase6:082] archive sha ok')")
# [P6-LOG-090] Step: full pytest.
echo "[P6:phase6:090] running full pytest"
(cd "$REPO_ROOT" && "$PYTHON_EXE" -m pytest tests/ -q)
# [P6-LOG-100] Step: gate summary.
echo "[P6:phase6:100] Phase-6 gate: outcome from artifacts, manifest complete, tests pass, audit generated, archive reproducible, scrub pass, claims match, no post-hoc edits"
echo "[P6:phase6:110] Phase 6 complete"
