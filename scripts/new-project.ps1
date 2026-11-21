<#
.SYNOPSIS
  Create a new project with the agent team already set up, from this template.

.EXAMPLE
  .\scripts\new-project.ps1 -Name my-tool
  .\scripts\new-project.ps1 -Name my-tool -Remote https://github.com/ArtyomSimitian/my-tool.git
  .\scripts\new-project.ps1 -Name my-tool -Packages pytest,requests

  By default the project is created next to this template folder (e.g. ...\GitHub\my-tool).
#>
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$ParentDir = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$Remote = "",
    [string[]]$Packages = @("pytest")
)
$ErrorActionPreference = "Stop"

$template = Split-Path $PSScriptRoot -Parent
$target = Join-Path $ParentDir $Name
if (Test-Path $target) { throw "$target already exists. Pick another name." }
if (-not (Test-Path (Join-Path $template ".claude\settings.json"))) {
    throw "The template has no .claude folder. Run once in the template: Move-Item _claude .claude"
}

Write-Host "Creating $target ..."
New-Item -ItemType Directory -Path $target | Out-Null
Get-ChildItem -Path $template -Force |
    Where-Object { $_.Name -notin @(".git", ".venv", "README.md", "_claude") } |
    ForEach-Object { Copy-Item -Path $_.FullName -Destination $target -Recurse -Force }

Remove-Item (Join-Path $target "scripts\new-project.ps1")
Copy-Item (Join-Path $target "SPEC.template.md") (Join-Path $target "SPEC.md")
Copy-Item (Join-Path $target ".work\status.initial.json") (Join-Path $target ".work\status.json") -Force

Push-Location $target
try {
    Write-Host "Creating virtual environment and installing: $($Packages -join ', '), streamlit, pandas ..."
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    & .\.venv\Scripts\python.exe -m pip install --quiet @Packages streamlit pandas

    git init -b main | Out-Null
    git add -A
    git commit --quiet -m "Scaffold agent team from template"
    if ($Remote) {
        git remote add origin $Remote
        git push -u origin main
    }
}
finally { Pop-Location }

Write-Host ""
Write-Host "Done. Open $target\AGENT_TEAM.md for the step-by-step checklist. In short:"
Write-Host "  1. Fill in $target\SPEC.md (delete SPEC.template.md when done)."
Write-Host "  2. Check 'Project commands' in CLAUDE.md and the allow list in .claude\settings.json."
Write-Host "  3. Terminal 2: .\scripts\start-monitor.ps1"
Write-Host "  4. Terminal 1: claude  -> accept trust -> 'Read WARMUP.md and run it as the Coordinator, following CLAUDE.md.'"
Write-Host "  5. .\scripts\reset-warmup.ps1, then a NEW claude session for the real build."
