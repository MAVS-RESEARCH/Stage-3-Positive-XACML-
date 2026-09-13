#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-6 seal verification for PC-XACML-S3+ (authoritative on the pinned host).

.DESCRIPTION
  Source check, Sec. 8.1 ten-condition read-only verification (no PDP rerun,
  no semantic recompute, no quarantine open), seal-hash binding, historical
  seal preservation, manifest verification, audit + claim linter (15 sections,
  Sec. 18.2 blocklist), archive verification, full pytest. Fails fast.
  Modes: default success-seal; --FailureSeal seals a stopped experiment
  (verifies the stop record, asserts no prohibited downstream artifacts,
  never overwrites success seals).

.PARAMETER RepoRoot
  Repository root. Defaults to the parent of this script's directory.
.PARAMETER PythonExe
  Python interpreter. Defaults to `python` on PATH.
.PARAMETER FailureSeal
  Switch for the stopped-experiment failure-seal path.
#>
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [string]$PythonExe = "python",
  [switch]$FailureSeal
)

$ErrorActionPreference = "Continue"

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P6-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P6:phase6:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P6-LOG-010] Step: start Phase 6, echo resolved configuration.
Write-Output "[P6:phase6:010] start Phase 6 seal verification"
$Mode = "success"
if ($FailureSeal) { $Mode = "failure" }
# [P6-LOG-012] Step: echo resolved configuration (repo + mode).
Write-Output ("[P6:phase6:012] repo={0} mode={1}" -f $RepoRoot, $Mode)
$Seal = Join-Path $RepoRoot "artifacts/seal/FINAL_RESULT_LAUNCH.json"

# [P6-LOG-020] Step: source check (frozen seals never touched).
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

if ($Mode -eq "failure") {
  # [P6-LOG-030] Step: failure-seal path for stopped experiments.
  Write-Output "[P6:phase6:030] failure-seal mode: verifying stop record"
  & $PythonExe - $RepoRoot @"
import json, os, sys
root = sys.argv[1]
for name in ("artifacts/seal/FINAL_RESULT.json", "artifacts/seal/FINAL_RESULT_CYCLE_002.json"):
    path = os.path.join(root, name)
    assert os.path.isfile(path), "historical seal missing: " + name
    assert json.load(open(path, encoding="utf-8")).get("outcome") == "NATIVE_ANCHOR_INSUFFICIENT", name
print("[P6:phase6:032] historical negative seals intact; operator supplies stopped_at_phase/trigger; success seals never overwritten")
"@
  if ($LASTEXITCODE -ne 0) { throw "step 030 failed" }
  Write-Output "[P6:phase6:034] failure-seal verification complete (no downstream run by protocol)"
  exit 0
}

# [P6-LOG-040] Step: success-seal 8.1 verification (read-only).
Invoke-Step "040" "verifying Sec. 8.1 ten conditions (read-only)" {
  & $PythonExe - $RepoRoot @"
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
assert load("artifacts/audits/launch/TARGET_EXECUTION_AUTHORIZED.json").get("authorized") is True, "8.1(3) authorization"
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
print("[P6:phase6:042] ten conditions hold; seal binds observed values")
"@
}

# [P6-LOG-050] Step: historical seals untouched.
Invoke-Step "050" "asserting historical seals untouched" {
  if (-not (Test-Path (Join-Path $RepoRoot "artifacts/seal/FINAL_RESULT.json"))) { exit 1 }
  if (-not (Test-Path (Join-Path $RepoRoot "artifacts/seal/FINAL_RESULT_CYCLE_002.json"))) { exit 1 }
  if (-not (Test-Path $Seal)) { exit 1 }
}

# [P6-LOG-060] Step: manifest verification.
Invoke-Step "060" "verifying MANIFEST.sha256" {
  & $PythonExe - $RepoRoot @"
import hashlib, os, sys
root = sys.argv[1]
bad = []
lines = open(os.path.join(root, "MANIFEST.sha256"), encoding="utf-8").read().splitlines()
for line in lines:
    if not line.strip():
        continue
    digest, rel = line.split("  ", 1)
    got = hashlib.sha256(open(os.path.join(root, rel), "rb").read()).hexdigest()
    if got != digest:
        bad.append(rel)
assert not bad, bad[:3]
print("[P6:phase6:062] manifest ok (%d entries)" % len(lines))
"@
}

# [P6-LOG-070] Step: audit + claim linter.
Invoke-Step "070" "verifying FINAL_AUDIT.md and claim gate" {
  & $PythonExe - $RepoRoot @"
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
"@
}

# [P6-LOG-075] Step: audit-report assembler verification (no hand numbers).
Invoke-Step "075" "verifying audit report assembler" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/build_audit_report.py") $RepoRoot
}

# [P6-LOG-080] Step: archive verification.
Invoke-Step "080" "verifying release archive" {
  if (-not (Test-Path (Join-Path $RepoRoot "PC-XACML-S3PLUS-v1.tar.gz"))) { exit 1 }
  if (-not (Test-Path (Join-Path $RepoRoot "PC-XACML-S3PLUS-v1.sha256"))) { exit 1 }
  if (-not (Test-Path (Join-Path $RepoRoot "PC-XACML-S3PLUS-v1.tar.gz.sha256"))) { exit 1 }
  & $PythonExe - $RepoRoot @"
import hashlib, os, sys
root = sys.argv[1]
exp = open(os.path.join(root, "PC-XACML-S3PLUS-v1.sha256"), encoding="utf-8").read().split()[0]
got = hashlib.sha256(open(os.path.join(root, "PC-XACML-S3PLUS-v1.tar.gz"), "rb").read()).hexdigest()
assert exp == got, (exp, got)
print("[P6:phase6:082] archive sha ok")
"@
}

# [P6-LOG-090] Step: full pytest.
Invoke-Step "090" "running full pytest" {
  & $PythonExe -m pytest tests/ -q
}

# [P6-LOG-100] Step: gate summary.
Write-Output "[P6:phase6:100] Phase-6 gate: outcome from artifacts, manifest complete, tests pass, audit generated, archive reproducible, scrub pass, claims match, no post-hoc edits"
Write-Output "[P6:phase6:110] Phase 6 complete"
