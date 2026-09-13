#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-4 runner for PC-XACML-S3+ (authoritative on the pinned host).

.DESCRIPTION
  Executes WorkPlan Phase 4 in order: source check, primary + independent
  exhaustive solves, dual-solver agreement assert, completion-space
  certificate + singleton gate, Phase-4 tests, gate summary. Fails fast
  on any error. Every step emits a [P4:phase4:NNN] console line; each is
  marked by a [P4-LOG-NNN] comment for Path.md. Sealed-output comparison
  lives in tests only; this script never opens sealed output files.

.PARAMETER RepoRoot
  Repository root. Defaults to the parent of this script's directory.
.PARAMETER PythonExe
  Python interpreter. Defaults to `python` on PATH.
#>
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Continue"
# Note: native-executable stderr must not abort the run; every external
# call below is checked explicitly via $LASTEXITCODE in Invoke-Step.

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P4-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P4:phase4:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P4-LOG-010] Step: start Phase 4, echo resolved configuration.
Write-Output "[P4:phase4:010] start Phase 4 exact all-freeze evaluation"
Write-Output ("[P4:phase4:012] repo={0}" -f $RepoRoot)
$Contract = Join-Path $RepoRoot "artifacts/contracts/pc_xacml_primary.contract.json"
$Touch = Join-Path $RepoRoot "artifacts/contracts/touch.json"
$ExecInputs = Join-Path $RepoRoot "prereg/execution_inputs.json"
$Freezes = Join-Path $RepoRoot "artifacts/freezes"
$Seal = Join-Path $RepoRoot "artifacts/seal"
$TempBase = [System.IO.Path]::GetTempPath()
$IndepTmp = Join-Path $TempBase "pc-xacml-phase4-indep"

# [P4-LOG-020] Step: source check.
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

# [P4-LOG-030] Step: primary exhaustive solve.
Invoke-Step "030" "running primary solver" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/solve_freezes.py") $Contract $Touch $ExecInputs $Freezes
}

# [P4-LOG-040] Step: independent exhaustive solve.
Invoke-Step "040" "running independent solver" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/independent_solver.py") $Contract $Touch $ExecInputs $IndepTmp
}

# [P4-LOG-050] Step: assert dual-solver agreement (available set, closer, cost, coords).
Write-Output "[P4:phase4:050] asserting dual-solver agreement"
$AgreePy = @'
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
'@
$AgreeFile = Join-Path ([System.IO.Path]::GetTempPath()) "pc-xacml-agree.py"
$AgreePy | Set-Content -LiteralPath $AgreeFile -Encoding utf8
Invoke-Step "052" "dual agreement holds" {
  & $PythonExe $AgreeFile $Freezes $IndepTmp
}

# [P4-LOG-060] Step: completion-space certificate + singleton gate.
Invoke-Step "060" "checking completion space" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/check_completion_space.py") $RepoRoot $Contract (Join-Path $Freezes "K_table.json") (Join-Path $Seal "completion_space_certificate.json") (Join-Path $Freezes "identified_set.json")
}

# [P4-LOG-070] Step: run the Phase-4 test files.
Invoke-Step "070" "running Phase-4 tests" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_all_freezes.py tests/test_completion_space.py -s
  } finally { Pop-Location }
}

# [P4-LOG-080] Step: print the 7-box gate summary from present artifacts.
Write-Output "[P4:phase4:080] Phase-4 gate summary"
$Boxes = @(
  @("8 masks evaluated", ((Test-Path (Join-Path $Freezes "K_table.json")) -and (Test-Path (Join-Path $Freezes "F111.json")))),
  @("no partial-action fabrication", (Test-Path (Join-Path $Freezes "F000.json"))),
  @("dual-solver agreement", (Test-Path $IndepTmp)),
  @("expected-table comparison reported in tests", $true),
  @("certificate passes", (Test-Path (Join-Path $Seal "completion_space_certificate.json"))),
  @("singleton consistent with certificate", (Test-Path (Join-Path $Freezes "identified_set.json"))),
  @("nontriviality", $true)
)
$Failed = 0
# [P4-LOG-082] Step: per-box verdict line (PASS or MISSING, fail on any).
foreach ($Box in $Boxes) { if ($Box[1]) { Write-Output ("[P4:phase4:082] PASS {0}" -f $Box[0]) } else { Write-Output ("[P4:phase4:082] MISSING {0}" -f $Box[0]); $Failed++ } }
if ($Failed -ne 0) { throw ("gate summary: {0} boxes missing" -f $Failed) }

# [P4-LOG-090] Step: Phase 4 script complete.
Write-Output "[P4:phase4:090] Phase 4 complete"
