$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Virtual environment not found. Run RUN_BENCHMARK.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"
streamlit run .\dashboard\app.py
