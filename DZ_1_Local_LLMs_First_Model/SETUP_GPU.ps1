$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "=== DZ 1 GPU environment setup ==="
Write-Host "Target: NVIDIA RTX 3060 12 GB / Windows / 4-bit NF4"
Write-Host ""

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        Write-Host "Creating Python 3.10 virtual environment..."
        py -3.10 -m venv .venv
    } else {
        Write-Host "Creating virtual environment with default python..."
        python -m venv .venv
    }
}

& ".\.venv\Scripts\Activate.ps1"

python -m pip install --upgrade pip wheel setuptools

# Use a CUDA 13.0 PyTorch wheel. NVIDIA driver CUDA 13.2 is backward compatible
# with this runtime, while bitsandbytes officially supports CUDA through 13.0.
python -m pip install --upgrade torch --index-url https://download.pytorch.org/whl/cu130

python -m pip install --upgrade -r requirements.txt

Write-Host ""
Write-Host "=== GPU verification ==="
python -c "import torch; print('Python/PyTorch OK'); print('torch =', torch.__version__); print('CUDA available =', torch.cuda.is_available()); print('torch CUDA runtime =', torch.version.cuda); print('GPU =', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO CUDA'); print('VRAM GB =', round(torch.cuda.get_device_properties(0).total_memory/1024**3,2) if torch.cuda.is_available() else 0)"

Write-Host ""
Write-Host "=== bitsandbytes verification ==="
python -c "import bitsandbytes as bnb; print('bitsandbytes =', bnb.__version__)"

Write-Host ""
Write-Host "SETUP COMPLETE."
Write-Host "Next: .\RUN_SMOKE_TEST.ps1"
