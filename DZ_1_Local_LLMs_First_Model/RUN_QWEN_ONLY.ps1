$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Environment not found. Run SETUP_GPU.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"

python .\src\benchmark.py --models Qwen1.5-7B
python .\src\evaluator.py
