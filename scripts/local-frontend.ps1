$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"

Set-Location $frontendDir

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev
