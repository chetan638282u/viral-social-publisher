$ErrorActionPreference = "Stop"

Set-Location -Path "$PSScriptRoot\.."

if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe -m viral_publisher telegram-request
} else {
    python -m viral_publisher telegram-request
}
