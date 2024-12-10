# Check if virtual environment exists, create if it doesn't
if (-not (Test-Path ".tools/.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .tools/.venv
}

# Activate virtual environment
. .tools/.venv/Scripts/Activate.ps1

# Install or update requirements
Write-Host "Checking requirements..."
python -m pip install -q -r .tools/requirements.txt

# Run pytest with explicit configuration
Write-Host "Running tests..."
python .tools/run_tests.py -c .tools/pyproject.toml

# Deactivate virtual environment
deactivate