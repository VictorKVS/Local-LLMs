$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Environment not found. Run SETUP_GPU.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"
python .\src\smoke_test.py
