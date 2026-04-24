# A2A Copilot - Kubernetes Deployment Script (PowerShell)

Write-Host "=== Deploying A2A Copilot to Kubernetes ===" -ForegroundColor Cyan

# 現在のディレクトリを保存
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Write-Host ""
Write-Host "Project root: $PROJECT_ROOT"
Write-Host ""

# Namespaceの作成
Write-Host ">>> Creating namespace..." -ForegroundColor Yellow
kubectl apply -f "$PROJECT_ROOT\k8s\namespace.yaml"
Write-Host ""

# GitHub Token Secretの確認
Write-Host ">>> Checking GitHub token secret..." -ForegroundColor Yellow
$secretExists = kubectl get secret github-token -n a2a-copilot 2>$null
if (-not $secretExists) {
    Write-Host "⚠ GitHub token secret not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the secret with your GitHub token:"
    Write-Host "  kubectl create secret generic github-token --from-literal=token=YOUR_TOKEN -n a2a-copilot"
    Write-Host ""
    $continue = Read-Host "Press Enter after creating the secret, or Ctrl+C to cancel"
}
Write-Host "✓ GitHub token secret exists" -ForegroundColor Green
Write-Host ""

# Dispatcherのデプロイ
Write-Host ">>> Deploying Dispatcher..." -ForegroundColor Yellow
kubectl apply -f "$PROJECT_ROOT\k8s\dispatcher.yaml"
Write-Host ""

# Agentsのデプロイ
Write-Host ">>> Deploying Weather Agent..." -ForegroundColor Yellow
kubectl apply -f "$PROJECT_ROOT\k8s\weather-agent.yaml"
Write-Host ""

Write-Host ">>> Deploying Calculator Agent..." -ForegroundColor Yellow
kubectl apply -f "$PROJECT_ROOT\k8s\calculator-agent.yaml"
Write-Host ""

# デプロイメント状態の確認
Write-Host "=== Deployment Status ===" -ForegroundColor Cyan
kubectl get all -n a2a-copilot
Write-Host ""

# Podsの起動を待機
Write-Host ">>> Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=dispatcher -n a2a-copilot --timeout=120s
kubectl wait --for=condition=ready pod -l app=a2a-agent -n a2a-copilot --timeout=120s
Write-Host ""

Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Check pod status: kubectl get pods -n a2a-copilot"
Write-Host "  2. View dispatcher logs: kubectl logs -f -l app=dispatcher -n a2a-copilot"
Write-Host "  3. Test the deployment: .\scripts\test-agents.ps1"
Write-Host "  4. Access dispatcher service: kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot"

# 元のディレクトリに戻る
Set-Location $SCRIPT_DIR
