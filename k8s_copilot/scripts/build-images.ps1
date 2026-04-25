# A2A Copilot - Docker Image Build Script (PowerShell)

Write-Host "=== Building A2A Copilot Docker Images ===" -ForegroundColor Cyan

# 現在のディレクトリを保存
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Write-Host ""
Write-Host "Project root: $PROJECT_ROOT"
Write-Host ""

# Dispatcher イメージのビルド
Write-Host ">>> Building Dispatcher image..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\dispatcher"
docker build -t a2a-dispatcher:latest .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dispatcher image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to build Dispatcher image" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Agent イメージのビルド
Write-Host ">>> Building Agent image..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\agents"
docker build -t a2a-agent:latest .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Agent image built successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to build Agent image" -ForegroundColor Red
    exit 1
}
Write-Host ""

# イメージ一覧を表示
Write-Host "=== Built Images ===" -ForegroundColor Cyan
docker images | Select-String "a2a-"
Write-Host ""

Write-Host "✓ All images built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Create GitHub token secret: kubectl create secret generic github-token --from-literal=token=YOUR_TOKEN -n a2a-copilot"
Write-Host "  2. Deploy to Kubernetes: .\scripts\deploy.ps1"

# 元のディレクトリに戻る
Set-Location $SCRIPT_DIR
