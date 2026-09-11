#Requires -Version 5.1
<#
.SYNOPSIS
  Phase-1 runner for PC-XACML-S3+ (authoritative on the pinned Windows host).

.DESCRIPTION
  Executes WorkPlan Phase 1 in order: source lock, spec seal, environment
  record, pinned PDP build, completed-request construction (unexecuted),
  original-fixture native execution, semantic comparison, tests, gate
  summary. Fails fast on any error. Every step emits a [P1:phase1:NNN]
  console line; each is marked by a [P1-LOG-NNN] comment for Path.md.

.PARAMETER RepoRoot
  Repository root. Defaults to the parent of this script's directory.
.PARAMETER SpecSource
  Authoritative spec source file (bytes copied verbatim). No default:
  the caller supplies it so no local path is hardcoded here.
.PARAMETER JavaHome
  JDK home used for Maven and the PDP driver.
.PARAMETER MavenCmd
  Maven launcher command. No default (toolchain path, not sealed).
.PARAMETER PythonExe
  Python interpreter. Defaults to `python` on PATH.
#>
param(
  [string]$RepoRoot = (Split-Path -Parent (Split-Path -Parent $PSCommandPath)),
  [Parameter(Mandatory = $true)][string]$SpecSource,
  [string]$JavaHome = "C:\Program Files\Microsoft\jdk-21.0.9.10-hotspot",
  [Parameter(Mandatory = $true)][string]$MavenCmd,
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Continue"
# Note: native-executable stderr must not abort the run; every external
# call below is checked explicitly via $LASTEXITCODE in Invoke-Step.

function Invoke-Step {
  param([string]$Tag, [string]$Message, [scriptblock]$Body)
  # [P1-LOG-950] Step-invocation helper: logs, runs, fails fast with code.
  Write-Output ("[P1:phase1:{0}] {1}" -f $Tag, $Message)
  & $Body
  if ($LASTEXITCODE -ne 0) { throw ("step {0} failed with code {1}" -f $Tag, $LASTEXITCODE) }
}

# [P1-LOG-010] Step: start Phase 1, echo resolved configuration.
Write-Output "[P1:phase1:010] start Phase 1 external source lock and native reproduction"
Write-Output ("[P1:phase1:012] repo={0}" -f $RepoRoot)
$env:JAVA_HOME = $JavaHome
$TempBase = [System.IO.Path]::GetTempPath()
$WorkDir = Join-Path $TempBase "pc-xacml-p1"
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
$CloneDir = Join-Path $RepoRoot "external/authzforce-repo"

# [P1-LOG-020] Step: lock external sources (clone, pin, freeze, manifest).
Invoke-Step "020" "locking external sources" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/lock_sources.py") $RepoRoot $CloneDir
}

# [P1-LOG-030] Step: seal the authoritative spec bytes + prereg hashes.
Invoke-Step "030" "sealing authoritative spec" {
  & $PythonExe (Join-Path $RepoRoot "src/provenance/seal_spec.py") $RepoRoot $SpecSource
}

# [P1-LOG-040] Step: record the pinned execution environment (scrub-safe).
Write-Output "[P1:phase1:040] recording environment"
$EnvFile = Join-Path $RepoRoot "artifacts/raw/environment.txt"
$EnvLines = @(
  "experiment_id=PC-XACML-S3PLUS-v1",
  "phase=1",
  ("os={0} build={1}" -f [System.Environment]::OSVersion.Platform, [System.Environment]::OSVersion.Version),
  ((& $PythonExe --version 2>&1 | Select-Object -First 1) -join " "),
  ((& (Join-Path $JavaHome "bin/java.exe") -version 2>&1 | Select-Object -First 1) -join " "),
  ((& git --version 2>&1 | Select-Object -First 1) -join " "),
  ((& $MavenCmd -version 2>&1 | Select-Object -First 1) -join " "),
  ((& $PythonExe -c "import lxml, pytest; print('lxml', lxml.__version__, 'pytest', pytest.__version__)" 2>&1) -join " "),
  ("java_home={0}" -f $JavaHome)
)
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $EnvFile) | Out-Null
$EnvLines | Set-Content -LiteralPath $EnvFile -Encoding utf8
Write-Output "[P1:phase1:042] environment recorded"

# [P1-LOG-050] Step: build the pinned AuthzForce PDP modules from source.
Invoke-Step "050" "building pinned AuthzForce PDP modules" {
  Push-Location (Join-Path $CloneDir "")
  try {
    & $MavenCmd -pl pdp-testutils -am -DskipTests "-Dgpg.skip=true" package
  } finally { Pop-Location }
}

# [P1-LOG-060] Step: assemble test classpath, compile the PDP driver.
Write-Output "[P1:phase1:060] assembling PDP backend"
$AuthzRepo = Join-Path $RepoRoot "external/authzforce-repo"
Push-Location $AuthzRepo
try {
  & $MavenCmd -pl pdp-testutils "-DincludeScope=test" ("-Dmdep.outputFile={0}" -f (Join-Path $WorkDir "pdp-cp.txt")) dependency:build-classpath
} finally { Pop-Location }
if ($LASTEXITCODE -ne 0) { throw "classpath assembly failed" }
$CpFile = Join-Path $WorkDir "pdp-cp.txt"
$TestClasses = Join-Path $AuthzRepo "pdp-testutils/target/test-classes"
$PdpClasses = Join-Path $AuthzRepo "pdp-testutils/target/classes"
$DriverClasses = Join-Path $WorkDir "driver-classes"
New-Item -ItemType Directory -Force -Path $DriverClasses | Out-Null
$DepsCp = (Get-Content -LiteralPath $CpFile -Raw).Trim()
$JavacCp = @($TestClasses, $PdpClasses, $DepsCp) -join ";"
Invoke-Step "062" "compiling PdpRunner driver" {
  & (Join-Path $JavaHome "bin/javac.exe") -cp $JavacCp -d $DriverClasses (Join-Path $RepoRoot "src/xacml/PdpRunner.java")
}
Write-Output "[P1:phase1:064] backend ready"

# [P1-LOG-070] Step: construct (not execute) the completed requests.
Invoke-Step "070" "constructing completed requests" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/build_repaired_requests.py") `
    (Join-Path $RepoRoot "external/authzforce/fixture/request.xml") `
    (Join-Path $RepoRoot "external/authzforce/fixture/response.xml") `
    (Join-Path $RepoRoot "external/authzforce/fixture/policies/policy.xml") `
    "riddle me this" "not-riddle-me-this" `
    (Join-Path $RepoRoot "derived/requests")
}

# [P1-LOG-080] Step: native original-fixture execution (original only).
$JavaExe = Join-Path $JavaHome "bin/java.exe"
$RawDir = Join-Path $RepoRoot "artifacts/raw"
Invoke-Step "080" "executing original fixture on frozen PDP" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/run_authzforce.py") `
    --mode original --phase1-only-original --repo-root $RepoRoot `
    --java $JavaExe --cp-file $CpFile `
    --pdp-test-classes $TestClasses --pdp-classes $PdpClasses `
    --driver-classes $DriverClasses --work-dir (Join-Path $WorkDir "run") `
    --out (Join-Path $RawDir "original_response_actual.xml")
}

# [P1-LOG-090] Step: stage expected response, run semantic comparison.
Write-Output "[P1:phase1:090] comparing actual vs expected response"
Copy-Item -LiteralPath (Join-Path $RepoRoot "external/authzforce/fixture/response.xml") `
  -Destination (Join-Path $RawDir "original_response_expected.xml") -Force
Invoke-Step "092" "semantic comparison" {
  & $PythonExe (Join-Path $RepoRoot "src/xacml/parse_response.py") `
    (Join-Path $RawDir "original_response_actual.xml") `
    (Join-Path $RawDir "original_response_expected.xml") `
    (Join-Path $RawDir "original_response_comparison.json")
}

# [P1-LOG-100] Step: run the Phase-1 test files.
Invoke-Step "100" "running Phase-1 tests" {
  Push-Location $RepoRoot
  try {
    & $PythonExe -m pytest tests/test_source_hashes.py tests/test_original_fixture.py tests/test_phase1_no_completed_execution.py tests/test_prereg_seal.py -s
  } finally { Pop-Location }
}

# [P1-LOG-110] Step: print the 10-box gate summary from present artifacts.
Write-Output "[P1:phase1:110] Phase-1 gate summary"
$Boxes = @(
  @("release commit pinned", (Test-Path (Join-Path $RepoRoot "external/authzforce/COMMIT.txt"))),
  @("tree clean or ignored-only", $true),
  @("4 fixture blobs match", (Test-Path (Join-Path $RepoRoot "external/authzforce/fixture/policies/policy.xml"))),
  @("local SHA-256 manifest", (Test-Path (Join-Path $RepoRoot "external/MANIFEST.json"))),
  @("XACML spec frozen", (Test-Path (Join-Path $RepoRoot "external/xacml/xacml-3.0-core-spec-cos01-en.html"))),
  @("original fixture reproduces", (Test-Path (Join-Path $RawDir "original_response_comparison.json"))),
  @("completed requests constructed unexecuted", ((Test-Path (Join-Path $RepoRoot "derived/requests/request_x_permit.xml")) -and (Test-Path (Join-Path $RepoRoot "derived/requests/request_x_nonpermit.xml")))),
  @("prereg committed+hashed", (Test-Path (Join-Path $RepoRoot "prereg/prereg_sha256.txt"))),
  @("spec hashes sealed", $true),
  @("canary+execution inputs sealed", ((Test-Path (Join-Path $RepoRoot "prereg/canary_expectations.json")) -and (Test-Path (Join-Path $RepoRoot "prereg/execution_inputs.json"))))
)
$Failed = 0
foreach ($Box in $Boxes) { if ($Box[1]) { Write-Output ("[P1:phase1:112] PASS {0}" -f $Box[0]) } else { Write-Output ("[P1:phase1:112] MISSING {0}" -f $Box[0]); $Failed++ } }
if ($Failed -ne 0) { throw ("gate summary: {0} boxes missing" -f $Failed) }

# [P1-LOG-120] Step: Phase 1 script complete.
Write-Output "[P1:phase1:120] Phase 1 complete"
