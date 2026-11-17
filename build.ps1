# Windows build script: runs the pytest suite, then packages dist/expense-mate-v1.0.zip.
# Usage:  .\build.ps1            (tests + package)
#         .\build.ps1 -SkipTests (package only)
param([switch]$SkipTests)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Get-Command python -ErrorAction SilentlyContinue) {
    $python = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $python = "py"
} else {
    Write-Error "Python was not found on PATH."
    exit 1
}

$buildArgs = @("build.py")
if ($SkipTests) { $buildArgs += "--skip-tests" }

& $python @buildArgs
exit $LASTEXITCODE
