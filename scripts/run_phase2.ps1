#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-2 runner for PC-XACML-S3+ (2A extraction, 2B packet, gated target audit).

.DESCRIPTION
  Modes: --primary performs 2A extraction, seals the blind packet, then
  either runs the target audit (only if the unlock conjunction holds:
  sealed verdict + H/P_R/Lambda/Atom all FIXED), records
  BLOCKED_PENDING_ADJUDICATION (exit 4, no completed-world execution),
  or records anchor failure (exit 2/3, failure-seal route, no
  completed-world execution). --reproduce verifies hashes and recomputes
  deterministic derivations without regenerating human judgment.
  --readjudicate rebuilds the packet for a fresh adjudication.
  Every step emits a [P2:phase2:NNN] console line; each is marked by a
  [P2-LOG-NNN] comment for Path.md.

.PARAMETER Mode
  primary, reproduce, or readjudicate.
.PARAMETER RepoRoot
  Repository root. Defaults to the parent of this script's directory.
.PARAMETER JavaHome
  JDK home used for the route-(a) probe and (post-unlock) target audit.
.PARAMETER MavenCmd
  Maven launcher command (used only if the PDP backend is absent).
.PARAMETER PythonExe
  Python interpreter. Defaults to `python` on PATH.
.PARAMETER WorkDir
  Scratch directory for backend artifacts (outside the repo).
#>
param(
  [string]$Mode = "primary",
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [string]$JavaHome = "C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot",
  [Parameter(Mandatory = $true)][string]$MavenCmd,
  [string]$PythonExe = "python",
  [string]$WorkDir = (Join-Path ([System.IO.Path]::GetTempPath()) "pc-xacml-p1")
)

$ErrorActionPreference = "Continue"
# Note: native-executable stderr must not abort the run; every external
# call below is checked explicitly via $LASTEXITCODE in Invoke-Step.

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P2-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P2:phase2:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

function Write-Status {
  param([string]$Status, [string]$Detail)
  # [P2-LOG-951] Status-file writer: records the Phase-2 outcome state.
  $Obj = @{phase = 2; mode = $Mode; status = $Status; detail = $Detail;
    utc = ([System.DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"))}
  $Obj | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $RepoRoot "artifacts/audits/phase2_status.json") -Encoding utf8
  Write-Output ("[P2:phase2:016] status={0} detail={1}" -f $Status, $Detail)
}

# [P2-LOG-010] Step: start Phase 2, echo mode and configuration.
Write-Output "[P2:phase2:010] start Phase 2 semantic anchor audit"
Write-Output ("[P2:phase2:012] mode={0} repo={1}" -f $Mode, $RepoRoot)
$env:JAVA_HOME = $JavaHome
$Derived = Join-Path $RepoRoot "derived"
$Audits = Join-Path $RepoRoot "artifacts/audits"
$Fixture = Join-Path $RepoRoot "external/authzforce/fixture"
$Manifest = Join-Path $RepoRoot "external/MANIFEST.json"
$ExecInputs = Join-Path $RepoRoot "prereg/execution_inputs.json"
New-Item -ItemType Directory -Force -Path $Audits | Out-Null

# [P2-LOG-020] Step: source check (verify seals before deriving).
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

if ($Mode -eq "readjudicate") {
  # [P2-LOG-025] Step: rebuild the packet for fresh adjudication.
  Invoke-Step "025" "rebuilding blind packet for readjudication" {
    & $PythonExe (Join-Path $RepoRoot "src/audit/blind_adjudication.py") --repo-root $RepoRoot --build-packet
  }
  Write-Output "[P2:phase2:120] readjudication packet ready"
  exit 0
}

# [P2-LOG-030] Step: ensure the PDP backend exists (route-a probe,
# post-unlock audit); rebuild from pinned source only if absent.
$CpFile = Join-Path $WorkDir "pdp-cp.txt"
$AuthzRepo = Join-Path $RepoRoot "external/authzforce-repo"
$TestClasses = Join-Path $AuthzRepo "pdp-testutils/target/test-classes"
$PdpClasses = Join-Path $AuthzRepo "pdp-testutils/target/classes"
$DriverClasses = Join-Path $WorkDir "driver-classes"
if (-not ((Test-Path $CpFile) -and (Test-Path (Join-Path $DriverClasses "PdpRunner.class")))) {
  Write-Output "[P2:phase2:030] backend absent, rebuilding from pinned source"
  Push-Location $AuthzRepo
  try {
    & $MavenCmd -pl pdp-testutils -am -DskipTests "-Dgpg.skip=true" package
  } finally { Pop-Location }
  if ($LASTEXITCODE -ne 0) { throw "backend rebuild failed" }
  Push-Location $AuthzRepo
  try {
    & $MavenCmd -pl pdp-testutils "-DincludeScope=test" ("-Dmdep.outputFile={0}" -f $CpFile) dependency:build-classpath
  } finally { Pop-Location }
  if ($LASTEXITCODE -ne 0) { throw "classpath assembly failed" }
  $DepsCp = (Get-Content -LiteralPath $CpFile -Raw).Trim()
  & (Join-Path $JavaHome "bin/javac.exe") -cp (@($TestClasses, $PdpClasses, $DepsCp) -join ";") -d $DriverClasses (Join-Path $RepoRoot "src/xacml/PdpRunner.java")
  if ($LASTEXITCODE -ne 0) { throw "driver compile failed" }
} else {
  Write-Output "[P2:phase2:030] backend present, reuse verified"
}

# [P2-LOG-040] Step: 2A policy projection + adequacy.
Invoke-Step "040" "projecting frozen policy" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/parse_policy.py") (Join-Path $Fixture "policies/policy.xml") $Manifest (Join-Path $Derived "policy_projection.json")
}
Invoke-Step "042" "certifying projection adequacy" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/check_policy_adequacy.py") (Join-Path $Derived "policy_projection.json") (Join-Path $Fixture "pdp.xml") $Manifest (Join-Path $Derived "policy_adequacy_certificate.json")
}

# [P2-LOG-050] Step: route-(a) probe + route-(b) equivalence proof.
Invoke-Step "050" "probing route-(a) availability" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/capture_resolved_context.py") $RepoRoot $JavaHome $PdpClasses $CpFile (Join-Path $Derived "route_a_probe.json")
}
Invoke-Step "052" "proving H-equivalence (route b)" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/prove_h_equivalence.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $Derived "policy_projection.json") (Join-Path $Derived "policy_adequacy_certificate.json") (Join-Path $Derived "route_a_probe.json") (Join-Path $Fixture "pdp.xml") (Join-Path $Derived "h_equivalence_proof.json")
}

# [P2-LOG-060] Step: derive H / P_R / Lambda / Atom records.
Invoke-Step "060" "deriving H objects" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_H.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $Derived "h_equivalence_proof.json") $Derived (Join-Path $RepoRoot "artifacts/audits/H_provenance.json")
}
Invoke-Step "062" "deriving P_R relation" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_PR.py") (Join-Path $Derived "policy_projection.json") (Join-Path $Derived "policy_adequacy_certificate.json") (Join-Path $Derived "pr_relation.json")
}
Invoke-Step "064" "recording Lambda" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_Lambda.py") (Join-Path $Fixture "pdp.xml") (Join-Path $Fixture "policies/policy.xml") $Manifest (Join-Path $Derived "lambda_record.json")
}
Invoke-Step "066" "proving Atom record" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_atom.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $RepoRoot "src/xacml/build_repaired_requests.py") $ExecInputs (Join-Path $Derived "atom_record.json")
}

# [P2-LOG-070] Step: assemble ledger, judge 2A completeness (0/2/4).
# Under Amendment 001, checker exit 4 (legacy human verdict absent) is
# the expected steady state: 2A assembly is complete and the operative
# blind gate is the amended model unanimity check below.
Write-Output "[P2:phase2:070] assembling anchor ledger"
& $PythonExe (Join-Path $RepoRoot "src/pc/check_anchor_completeness.py") $RepoRoot $Derived
$CheckerCode = $LASTEXITCODE
Write-Output ("[P2:phase2:072] checker exit={0}" -f $CheckerCode)
if ($CheckerCode -eq 2) {
  Write-Status "ANCHOR_FAILURE" "checker reported ambiguous/failed anchors; failure-seal route, no completed-world execution"
  throw "anchor failure: failure-seal route"
}

# [P2-LOG-080] Step: ensure the sealed blind auditor packet.
# Amendment-001 rule: the sealed packet is immutable once built. Rebuild
# ONLY if absent or corrupt (or via --readjudicate); otherwise verify
# and reuse, so the amendment-referenced packet hash never drifts.
Write-Output "[P2:phase2:080] ensuring sealed blind packet"
& $PythonExe (Join-Path $RepoRoot "scripts/repro_compare.py") packet-verify $RepoRoot
if ($LASTEXITCODE -ne 0) {
  Write-Output "[P2:phase2:081] packet absent or corrupt, rebuilding"
  Invoke-Step "080" "building blind auditor packet" {
    & $PythonExe (Join-Path $RepoRoot "src/audit/blind_adjudication.py") --repo-root $RepoRoot --build-packet
  }
} else {
  Write-Output "[P2:phase2:081] sealed packet verified, reuse (no rebuild)"
}

if ($Mode -eq "reproduce") {
  # [P2-LOG-085] Step: reproduce mode verifies + recomputes, no regen.
  Write-Output "[P2:phase2:085] reproduce mode: verify + recompute"
  & $PythonExe (Join-Path $RepoRoot "src/audit/model_adjudication.py") --repo-root $RepoRoot --check-amendment
  if ($LASTEXITCODE -ne 0) { throw "reproduce: amendment seal invalid" }
  $ReproDir = Join-Path $WorkDir "phase2-repro"
  if (Test-Path $ReproDir) { Remove-Item -Recurse -Force $ReproDir }
  New-Item -ItemType Directory -Force -Path $ReproDir | Out-Null
  & $PythonExe (Join-Path $RepoRoot "src/xacml/parse_policy.py") (Join-Path $Fixture "policies/policy.xml") $Manifest (Join-Path $ReproDir "policy_projection.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: projection failed" }
  & $PythonExe (Join-Path $RepoRoot "src/xacml/check_policy_adequacy.py") (Join-Path $ReproDir "policy_projection.json") (Join-Path $Fixture "pdp.xml") $Manifest (Join-Path $ReproDir "policy_adequacy_certificate.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: adequacy failed" }
  & $PythonExe (Join-Path $RepoRoot "src/xacml/capture_resolved_context.py") $RepoRoot $JavaHome $PdpClasses $CpFile (Join-Path $ReproDir "route_a_probe.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: route-a failed" }
  & $PythonExe (Join-Path $RepoRoot "src/pc/prove_h_equivalence.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $ReproDir "policy_projection.json") (Join-Path $ReproDir "policy_adequacy_certificate.json") (Join-Path $ReproDir "route_a_probe.json") (Join-Path $Fixture "pdp.xml") (Join-Path $ReproDir "h_equivalence_proof.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: equivalence failed" }
  New-Item -ItemType Directory -Force -Path (Join-Path $ReproDir "h") | Out-Null
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_H.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $ReproDir "h_equivalence_proof.json") (Join-Path $ReproDir "h") (Join-Path $ReproDir "H_provenance.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: H failed" }
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_PR.py") (Join-Path $ReproDir "policy_projection.json") (Join-Path $ReproDir "policy_adequacy_certificate.json") (Join-Path $ReproDir "pr_relation.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: PR failed" }
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_Lambda.py") (Join-Path $Fixture "pdp.xml") (Join-Path $Fixture "policies/policy.xml") $Manifest (Join-Path $ReproDir "lambda_record.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: Lambda failed" }
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_atom.py") (Join-Path $Fixture "request.xml") (Join-Path $Derived "requests/request_x_permit.xml") (Join-Path $Derived "requests/request_x_nonpermit.xml") (Join-Path $RepoRoot "src/xacml/build_repaired_requests.py") $ExecInputs (Join-Path $ReproDir "atom_record.json")
  if ($LASTEXITCODE -ne 0) { throw "reproduce: Atom failed" }
  $env:PC_REPRO_DIR = $ReproDir
  $env:PC_REPO_ROOT = $RepoRoot
  & $PythonExe (Join-Path $RepoRoot "scripts/repro_compare.py") deriv-compare $RepoRoot $ReproDir
  if ($LASTEXITCODE -ne 0) { throw "reproduce: recomputation mismatch" }
  & $PythonExe (Join-Path $RepoRoot "src/pc/check_anchor_completeness.py") $RepoRoot (Join-Path $ReproDir "ledger")
  if ($LASTEXITCODE -ne 4) { throw "reproduce: ledger rebuild did not block as expected" }
  & $PythonExe (Join-Path $RepoRoot "scripts/repro_compare.py") ledger-compare $RepoRoot $ReproDir
  if ($LASTEXITCODE -ne 0) { throw "reproduce: ledger mismatch" }
  & $PythonExe (Join-Path $RepoRoot "scripts/repro_compare.py") packet-verify $RepoRoot
  if ($LASTEXITCODE -ne 0) { throw "reproduce: packet mismatch" }
  Write-Status "REPRODUCED" "hashes verified; deterministic derivations recomputed without regenerating human judgment"
  Write-Output "[P2:phase2:120] Phase 2 reproduce complete"
  exit 0
}

# [P2-LOG-090] Step: judge the amended model unlock before any execution.
# Amendment 001 replaces the human-only unlock: unanimous FIXED across
# three valid cold-model adjudications is required (exit 0). Exit 4 =
# blocked pending (fewer than three valid records); exit 5 = invalid
# record (blocked class); exit 3 = valid but nonunanimous verdicts =
# substantive non-support, failure-seal route, zero execution.
Write-Output "[P2:phase2:090] judging amended model unlock"
& $PythonExe (Join-Path $RepoRoot "src/audit/model_adjudication.py") --repo-root $RepoRoot --assert-model-unlock
$UnlockCode = $LASTEXITCODE
if ($UnlockCode -eq 4) {
  Write-Status "BLOCKED_PENDING_MODEL_ADJUDICATION" "fewer than three valid cold-model records; completed worlds never executed; target audit locked"
  Write-Output "[P2:phase2:120] Phase 2 blocked pending model adjudication (exit 4)"
  exit 4
}
if ($UnlockCode -eq 5) {
  Write-Status "MODEL_ADJUDICATION_INVALID" "malformed/incomplete model record; blocked class, not semantic failure; completed worlds never executed"
  Write-Output "[P2:phase2:120] Phase 2 model adjudication invalid (exit 5)"
  exit 5
}
if ($UnlockCode -eq 3) {
  Write-Status "MODEL_ADJUDICATION_NONUNANIMOUS" "valid verdict below FIXED on at least one anchor: NATIVE_ANCHOR_INSUFFICIENT; failure-seal route; completed worlds never executed"
  throw "anchor insufficiency: failure-seal route"
}
if ($UnlockCode -ne 0) { throw ("unlock judge failed with code {0}" -f $UnlockCode) }

# [P2-LOG-100] Step: unlocked target audit (first completed execution).
Write-Output "[P2:phase2:100] unlock holds: running target audit"
# Hardening RS003-B01: deployment-set gate inside the measured interval,
# after unlock and before the first completed evaluation.
Write-Output "[P2:phase2:095] gating staged deployment set"
& $PythonExe (Join-Path $RepoRoot "src/audit/verify_deployment_set.py") --repo-root $RepoRoot --check --fixture-dir (Join-Path $Fixture "policies") --listing (Join-Path $RepoRoot "artifacts/audits/semantic_hardening/rounds/HARDENING_ROUND_003/evidence/policy_dir_listing.json")
if ($LASTEXITCODE -ne 0) { throw "deployment-set gate failed" }
& $PythonExe (Join-Path $RepoRoot "src/audit/verify_deployment_set.py") --repo-root $RepoRoot --disjoint --out-dir (Join-Path $Derived "requests") --policies-dir (Join-Path $Fixture "policies")
if ($LASTEXITCODE -ne 0) { throw "deployment disjointness gate failed" }
$JavaExe = Join-Path $JavaHome "bin/java.exe"
foreach ($World in @("x_permit", "x_nonpermit")) {
  $Req = Join-Path $Derived ("requests/request_{0}.xml" -f $World)
  $Out = Join-Path $RepoRoot ("artifacts/raw/target_{0}_actual.xml" -f $World)
  Invoke-Step ("102-{0}" -f $World) ("target audit {0}" -f $World) {
    & $PythonExe (Join-Path $RepoRoot "src/xacml/run_authzforce.py") --mode completed --world $World --request $Req --repo-root $RepoRoot --java $JavaExe --cp-file $CpFile --pdp-test-classes $TestClasses --pdp-classes $PdpClasses --driver-classes $DriverClasses --work-dir (Join-Path $WorkDir "target") --out $Out
  }
}

# [P2-LOG-110] Step: run the Phase-2 test files.
Invoke-Step "110" "running Phase-2 tests" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_policy_projection.py tests/test_policy_adequacy.py tests/test_h_equivalence.py tests/test_anchor_completeness.py tests/test_blind_adjudication.py tests/test_completed_world_decisions.py -s
  } finally { Pop-Location }
}

# [P2-LOG-115] Step: seal the Phase-2 output manifest.
Write-Output "[P2:phase2:115] sealing Phase-2 outputs"
$env:PC_REPO_ROOT = $RepoRoot
& $PythonExe -c "import hashlib,json,os; r=os.environ['PC_REPO_ROOT']; files=['derived/policy_projection.json','derived/policy_adequacy_certificate.json','derived/route_a_probe.json','derived/h_equivalence_proof.json','derived/H_initial.json','derived/H_permit.json','derived/H_nonpermit.json','derived/pr_relation.json','derived/lambda_record.json','derived/atom_record.json','derived/anchor_ledger.json','derived/anchor_ledger.md']; d={f:hashlib.sha256(open(os.path.join(r,f),'rb').read()).hexdigest() for f in files}; json.dump({'phase':2,'files':d},open(os.path.join(r,'artifacts/audits/phase2_seal.json'),'w'),indent=2,sort_keys=True)"
if ($LASTEXITCODE -ne 0) { throw "phase-2 seal failed" }

Write-Status "COMPLETE_POSITIVE_ELIGIBLE" "unlock held; target audit executed; ledger complete"
# [P2-LOG-120] Step: Phase 2 script complete.
Write-Output "[P2:phase2:120] Phase 2 complete"
