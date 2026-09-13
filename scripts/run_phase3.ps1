#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-3 runner for PC-XACML-S3+ (authoritative on the pinned host).

.DESCRIPTION
  Mechanical PC contract compilation: source check, contract compile,
  primary touch derivation, independent rederivation with byte compare,
  no-manual-label audit, Phase-3 tests, manifest seal. Fails fast.
  Every step emits a [P3:phase3:NNN] console line; each is marked by a
  [P3-LOG-NNN] comment for Path.md.

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
  # [P3-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P3:phase3:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P3-LOG-010] Step: start Phase 3, echo resolved configuration.
Write-Output "[P3:phase3:010] start Phase 3 mechanical contract compilation"
Write-Output ("[P3:phase3:012] repo={0}" -f $RepoRoot)

# [P3-LOG-020] Step: source check (verify seals before deriving).
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

# [P3-LOG-025] Step: models self-check (canonical/no-touch invariant).
Invoke-Step "025" "checking PC data models" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/models.py") --self-check
}

# [P3-LOG-030] Step: compile the primary contract.
Invoke-Step "030" "compiling primary contract" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/compile_contract.py") $RepoRoot (Join-Path $RepoRoot "artifacts/contracts/pc_xacml_primary.contract.json")
}

# [P3-LOG-040] Step: derive touch (primary mechanical derivation).
Invoke-Step "040" "deriving touch (primary)" {
  & $PythonExe (Join-Path $RepoRoot "src/pc/derive_touch.py") (Join-Path $RepoRoot "artifacts/contracts/pc_xacml_primary.contract.json") (Join-Path $RepoRoot "artifacts/contracts/touch.json")
}

# [P3-LOG-050] Step: rederive touch (independent) and byte-compare.
$TmpTouch = Join-Path ([System.IO.Path]::GetTempPath()) "pc-xacml-touch-indep.json"
Invoke-Step "050" "rederiving touch (independent)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/independent_touch.py") (Join-Path $RepoRoot "artifacts/contracts/pc_xacml_primary.contract.json") $TmpTouch
}
Write-Output "[P3:phase3:052] comparing touch bytes"
$PrimaryBytes = [System.IO.File]::ReadAllBytes((Join-Path $RepoRoot "artifacts/contracts/touch.json"))
$IndepBytes = [System.IO.File]::ReadAllBytes($TmpTouch)
if ([System.BitConverter]::ToString($PrimaryBytes) -ne [System.BitConverter]::ToString($IndepBytes)) { throw "dual touch mismatch" }
Write-Output "[P3:phase3:054] dual touch agreement ok"

# [P3-LOG-060] Step: no-manual-label static audit.
Invoke-Step "060" "auditing no-manual-labels" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/check_no_manual_labels.py") $RepoRoot
}

# [P3-LOG-070] Step: run the Phase-3 test files.
Invoke-Step "070" "running Phase-3 tests" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_touch_derivation.py tests/test_no_manual_touch_labels.py -s
  } finally { Pop-Location }
}

# [P3-LOG-080] Step: seal the Phase-3 manifest.
Write-Output "[P3:phase3:080] sealing Phase-3 manifest"
$env:PC_REPO_ROOT = $RepoRoot
& $PythonExe -c "import hashlib,json,os; r=os.environ['PC_REPO_ROOT']; files=['artifacts/contracts/pc_xacml_primary.contract.json','artifacts/contracts/touch.json','derived/anchor_ledger.json','external/MANIFEST.json','prereg/execution_inputs.json']; d={f:hashlib.sha256(open(os.path.join(r,f),'rb').read()).hexdigest() for f in files}; m={'phase':3,'contract_sha256':d['artifacts/contracts/pc_xacml_primary.contract.json'],'touch_sha256':d['artifacts/contracts/touch.json'],'anchor_ledger_sha256':d['derived/anchor_ledger.json'],'external_manifest_sha256':d['external/MANIFEST.json'],'execution_inputs_sha256':d['prereg/execution_inputs.json'],'files':d,'derivation':{'compiler':'src/pc/compile_contract.py','primary':'src/pc/derive_touch.py','independent':'src/audit/independent_touch.py'}}; json.dump(m,open(os.path.join(r,'artifacts/seal/phase3_manifest.json'),'w'),indent=2,sort_keys=True)"
if ($LASTEXITCODE -ne 0) { throw "phase-3 seal failed" }
Write-Output "[P3:phase3:082] manifest sealed"

# [P3-LOG-090] Step: gate summary.
Write-Output "[P3:phase3:090] Phase-3 gate: contract, S0 open, successors closed, touch mechanical, dual agreement, no manual labels, hashes sealed"
# [P3-LOG-100] Step: Phase 3 script complete.
Write-Output "[P3:phase3:100] Phase 3 complete"
