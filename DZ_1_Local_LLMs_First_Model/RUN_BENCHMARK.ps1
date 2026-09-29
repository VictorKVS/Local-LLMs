$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Environment not found. Run SETUP_GPU.ps1 first."
}

& ".\.venv\Scripts\Activate.ps1"

python -c "import torch; assert torch.cuda.is_available(), 'CUDA unavailable'; print('GPU:', torch.cuda.get_device_name(0)); print('CUDA runtime:', torch.version.cuda)"

python .\src\benchmark.py
python .\src\evaluator.py

Write-Host ""
Write-Host "READY:"
Write-Host "  data\raw_results.csv"
Write-Host "  data\evaluated_results.csv"
