#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-5 runner for PC-XACML-S3+ (authoritative on the pinned host).

.DESCRIPTION
  Falsification, sensitivity, anti-circularity audit: source check,
  sealed-expectation presence check (hash only, never opened during
  execution), raw canary execution via frozen PDP backend (PdpRunner
  directly, temp copies only), post-execution comparison via
  compare_canary_outcomes.py, perturbations, interface-change control,
  cost sweep, negative-world sweep, ablations, label injection, leakage
  audit, clean reproduction, Phase-5 tests, gate summary. Fails fast.
  Every step emits a [P5:phase5:NNN] console line; each is marked by a
  [P5-LOG-NNN] comment for Path.md. Frozen external/ never mutated.

.PARAMETER RepoRoot
  Repository root. Defaults to the parent of this script's directory.
.PARAMETER PythonExe
  Python interpreter. Defaults to `python` on PATH.
.PARAMETER JavaHome
  JDK home for the frozen PDP backend.
.PARAMETER WorkDir
  Scratch directory for backend artifacts (outside the repo).
#>
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [string]$PythonExe = "python",
  [string]$JavaHome = "C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot",
  [string]$WorkDir = (Join-Path ([System.IO.Path]::GetTempPath()) "pc-xacml-p1")
)

$ErrorActionPreference = "Continue"
# Note: native-executable stderr must not abort the run; every external
# call below is checked explicitly via $LASTEXITCODE in Invoke-Step.

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P5-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P5:phase5:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P5-LOG-010] Step: start Phase 5, echo resolved configuration.
Write-Output "[P5:phase5:010] start Phase 5 falsification, sensitivity, anti-circularity audit"
Write-Output ("[P5:phase5:012] repo={0}" -f $RepoRoot)
$Audits = Join-Path $RepoRoot "artifacts/audits"
$JavaExe = Join-Path $JavaHome "bin/java.exe"
$CpFile = Join-Path $WorkDir "pdp-cp.txt"
$AuthzRepo = Join-Path $RepoRoot "external/authzforce-repo"
$TestClasses = Join-Path $AuthzRepo "pdp-testutils/target/test-classes"
$PdpClasses = Join-Path $AuthzRepo "pdp-testutils/target/classes"
$DriverClasses = Join-Path $WorkDir "driver-classes"
New-Item -ItemType Directory -Force -Path $Audits | Out-Null

# [P5-LOG-020] Step: source check (verify seals before any control).
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

# [P5-LOG-022] Step: sealed-expectation presence check (hash only, never opened).
Write-Output "[P5:phase5:022] checking sealed canary expectations exist (hash only)"
$SealFile = Join-Path $RepoRoot "prereg/prereg_sha256.txt"
$SealText = Get-Content -LiteralPath $SealFile -Raw
if (-not ($SealText -match "canary_expectations\.json")) { throw "sealed canary expectations hash missing" }
$CanaryPath = Join-Path $RepoRoot "prereg/canary_expectations.json"
if (-not (Test-Path $CanaryPath)) { throw "sealed canary expectations file missing" }
# [P5-LOG-024] Step: presence confirmed without opening sealed values.
Write-Output "[P5:phase5:024] sealed expectations present (not opened during execution)"

# [P5-LOG-030] Step: backend presence check (frozen PDP, no rebuild).
Write-Output "[P5:phase5:030] checking frozen PDP backend"
if (-not ((Test-Path $CpFile) -and (Test-Path (Join-Path $DriverClasses "PdpRunner.class")) -and (Test-Path $TestClasses) -and (Test-Path $PdpClasses))) { throw "frozen PDP backend absent" }
Write-Output "[P5:phase5:032] backend present"

# [P5-LOG-040] Step: 5.1 hash-corruption control (temp copies only).
Invoke-Step "040" "running hash-corruption control (5.1)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits corruption
}

# [P5-LOG-050] Step: 5.2-5.5 + 5.9 raw canary execution (frozen PDP directly, temp copies).
Invoke-Step "050" "running canary raw execution (5.2-5.5, 5.9)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits canary_raw $JavaExe $CpFile $TestClasses $PdpClasses $DriverClasses
}

# [P5-LOG-052] Step: post-execution comparison (only step allowed to open expectations).
Invoke-Step "052" "comparing canary raws vs sealed expectations" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/compare_canary_outcomes.py") $RepoRoot $Audits
}

# [P5-LOG-060] Step: 5.6 preserving perturbations + 5.7 interface-change control.
Invoke-Step "060" "running preserving perturbations (5.6) + interface change (5.7)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits perturbation $JavaExe $CpFile $TestClasses $PdpClasses $DriverClasses
}

# [P5-LOG-070] Step: 5.8 cost sweep.
Invoke-Step "070" "running cost sweep (5.8)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits cost
}

# [P5-LOG-080] Step: 5.9 negative-world sweep summary.
Invoke-Step "080" "running negative-world sweep (5.9)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits negative
}

# [P5-LOG-090] Step: 5.10 anchor ablations.
Invoke-Step "090" "running anchor ablations (5.10)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits ablation
}

# [P5-LOG-100] Step: 5.11 label injection.
Invoke-Step "100" "running label-injection control (5.11)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits label
}

# [P5-LOG-110] Step: 5.12 leakage audit.
Invoke-Step "110" "running leakage audit (5.12)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits leakage
}

# [P5-LOG-120] Step: 5.13 clean reproduction.
Invoke-Step "120" "running clean reproduction (5.13)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/phase5_execute.py") $RepoRoot $Audits cleanrepro $JavaExe $CpFile $TestClasses $PdpClasses $DriverClasses
}

# [P5-LOG-130] Step: run the Phase-5 test files.
Invoke-Step "130" "running Phase-5 tests" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_parser_corruptions.py tests/test_cost_robustness.py tests/test_interface_preserving_mutations.py tests/test_anchor_ablation.py tests/test_clean_reproduction.py -s
  } finally { Pop-Location }
}

# [P5-LOG-140] Step: print the 13-box gate summary from present artifacts.
Write-Output "[P5:phase5:140] Phase-5 gate summary"
$Boxes = @(
  @("5.1 corruptions detected", ((Test-Path (Join-Path $Audits "corruption_pdp.json")) -and (Test-Path (Join-Path $Audits "corruption_spec.json")))),
  @("5.2 mustbepresent canary", (Test-Path (Join-Path $Audits "canary_mustbepresent_removed_comparison.json"))),
  @("5.3 wrong-category canary", (Test-Path (Join-Path $Audits "canary_wrong_category_comparison.json"))),
  @("5.4 wrong-datatype canary", (Test-Path (Join-Path $Audits "canary_wrong_datatype_comparison.json"))),
  @("5.5 projection canary", (Test-Path (Join-Path $Audits "canary_irrelevant_extra_attribute_comparison.json"))),
  @("5.6 perturbations preserve", (Test-Path (Join-Path $Audits "perturbation_whitespace.json"))),
  @("5.7 interface change rejected", (Test-Path (Join-Path $Audits "perturbation_interface_change.json"))),
  @("5.8 cost sweep invariant", (Test-Path (Join-Path $Audits "cost_sweep.json"))),
  @("5.9 negative-world sweep", (Test-Path (Join-Path $Audits "negative_world_sweep.json"))),
  @("5.10 ablations refuse", (Test-Path (Join-Path $Audits "ablation_H.json"))),
  @("5.11 label injection detected", (Test-Path (Join-Path $Audits "label_injection.json"))),
  @("5.12 leakage passes", (Test-Path (Join-Path $Audits "leakage_graph.json"))),
  @("5.13 clean repro matches", (Test-Path (Join-Path $Audits "clean_repro.json")))
)
$Failed = 0
# [P5-LOG-142] Step: per-box verdict line (PASS or MISSING, fail on any).
foreach ($Box in $Boxes) { if ($Box[1]) { Write-Output ("[P5:phase5:142] PASS {0}" -f $Box[0]) } else { Write-Output ("[P5:phase5:142] MISSING {0}" -f $Box[0]); $Failed++ } }
if ($Failed -ne 0) { throw ("gate summary: {0} boxes missing" -f $Failed) }

# [P5-LOG-150] Step: Phase 5 script complete.
Write-Output "[P5:phase5:150] Phase 5 complete"
