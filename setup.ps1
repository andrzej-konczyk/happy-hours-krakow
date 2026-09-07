$ErrorActionPreference = "Stop"

function Get-PythonLauncher {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    return $null
}

$python = Get-PythonLauncher
if (-not $python) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "Python is not installed and winget is unavailable. Install Python 3.11+ from https://www.python.org/downloads/windows/"
    }

    Write-Host "Installing Python 3.13 with winget..."
    winget install --id Python.Python.3.13 --exact --scope user --accept-source-agreements --accept-package-agreements
    $python = Get-PythonLauncher
    if (-not $python) {
        throw "Python was installed. Close and reopen PowerShell, then run .\setup.ps1 again."
    }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $python -m venv .venv
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Add your Supabase credentials before seeding."
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Edit .env, then run:"
Write-Host "  .\.venv\Scripts\python.exe seed_data.py"
Write-Host "  .\.venv\Scripts\python.exe run_pipeline.py"
Write-Host "  .\.venv\Scripts\python.exe -m uvicorn main:app --reload"
