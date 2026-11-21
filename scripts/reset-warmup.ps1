<#
.SYNOPSIS
  Remove everything the warm-up created, reset the shared state and budget, and commit.
  Run it after the warm-up and before starting the real build in a new claude session.
#>
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$paths = @(
    "warmup", "tests\test_warmup.py", "pyproject.toml", "WARMUP.md",
    ".work\plan.md", ".work\log.md", ".work\warmup_report.md", ".work\notes",
    ".work\events.jsonl", ".work\guard_count.json",
    "FINAL_REPORT.md", "DECISIONS.md"
)
foreach ($p in $paths) {
    if (Test-Path $p) { Remove-Item -Recurse -Force $p; Write-Host "removed $p" }
}
if ((Test-Path "tests") -and -not (Get-ChildItem "tests" -Recurse -File | Where-Object { $_.Name -ne "__init__.py" })) {
    Remove-Item -Recurse -Force "tests"; Write-Host "removed empty tests\"
}
Copy-Item ".work\status.initial.json" ".work\status.json" -Force

git add -A
git commit --quiet -m "Remove warm-up"
git status --short
Write-Host "Warm-up cleared. Budget counter reset. Start a NEW claude session for the real build."
