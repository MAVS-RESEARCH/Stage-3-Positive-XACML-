#Requires -Version 5.1
<#
.SYNOPSIS
  Reproduction replay for PC-XACML-S3+ (authoritative on the pinned host).

.DESCRIPTION
  Replays every phase in verify-only modes from a checkout: sealed human/
  model judgments are verified by hash, never regenerated. Fails fast.
  Every step emits a [P6:repro:NNN] console line; each is marked by a
  [P6-LOG-RNN] comment for Path.md.
#>
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Continue"

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P6-LOG-R95] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P6:repro:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P6-LOG-R10] Step: start reproduction replay, resolve arguments.
Write-Output "[P6:repro:010] start reproduction replay"
# [P6-LOG-R12] Step: echo the resolved repository root.
Write-Output ("[P6:repro:012] repo={0}" -f $RepoRoot)

# [P6-LOG-R20] Step: sealed sources (no re-lock, verify only).
Invoke-Step "020" "verifying sealed sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/verify_sources.py") $RepoRoot
}

# [P6-LOG-R30] Step: sealed packet and launch records (hash verify only).
Invoke-Step "030" "verifying sealed packet and launch records" {
  & $PythonExe (Join-Path $RepoRoot "scripts/repro_compare.py") packet-verify $RepoRoot
}
Invoke-Step "032" "reporting launch status (no re-freeze)" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/launch_freeze.py") --repo-root $RepoRoot --status
}

# [P6-LOG-R40] Step: deterministic derivations re-checked via test suites.
Invoke-Step "040" "running derivation test suites" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_touch_derivation.py tests/test_no_manual_touch_labels.py tests/test_all_freezes.py tests/test_completion_space.py -q
  } finally { Pop-Location }
}

# [P6-LOG-R50] Step: seal and manifest presence (hash verify only).
Invoke-Step "050" "verifying seal and audit report" {
  & $PythonExe (Join-Path $RepoRoot "src/audit/build_audit_report.py") $RepoRoot
}
Invoke-Step "052" "asserting seal and manifest presence" {
  if (-not (Test-Path (Join-Path $RepoRoot "artifacts/seal/FINAL_RESULT_LAUNCH.json"))) { exit 1 }
  if (-not (Test-Path (Join-Path $RepoRoot "MANIFEST.sha256"))) { exit 1 }
}

# [P6-LOG-R60] Step: reproduction replay complete.
Write-Output "[P6:repro:060] reproduction replay complete"
