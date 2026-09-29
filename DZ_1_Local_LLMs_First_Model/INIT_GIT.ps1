$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".git")) {
    git init -b main
}

git add .
git commit -m "feat: add DZ 1 multi-model local LLM benchmark and dashboard"

Write-Host ""
Write-Host "Local commit created."
Write-Host "Parent course repo can include this folder as part of Local-LLMs."
