#!/usr/bin/env pwsh
# gh-copilot Service へ kubectl port-forward を起動し、
# 環境変数 COPILOT_CLI_URL=localhost:4321 をセットするスクリプト
#
# 使い方:
#   & k8s/set-url.ps1
#   または
#   . k8s/set-url.ps1  # ドットソースで実行して環境変数を現在のセッションに適用
#
# 注意: Rancher Desktop on macOS/Windows では LoadBalancer の EXTERNAL-IP に
#       ホストから直接アクセスできないため port-forward を使用します。

$ErrorActionPreference = 'Stop'

$LOCAL_PORT = 4321

# 既存の port-forward プロセスを停止する
$existingProcess = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ProcessName -eq 'kubectl' -and $_.CommandLine -like "*port-forward*gh-copilot*$LOCAL_PORT*"
}

if ($existingProcess) {
    Stop-Process -Id $existingProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "既存の port-forward (PID: $($existingProcess.Id)) を停止しました。" -ForegroundColor Yellow
}

# Pod が Running になるまで待つ
Write-Host "Pod の起動を待機中..." -ForegroundColor Cyan
for ($i = 1; $i -le 10; $i++) {
    $status = kubectl get pods -n copilot-sdk -l app=copilot-sdk `
        -o jsonpath='{.items[0].status.phase}' 2>$null
    
    if ($status -eq "Running") {
        break
    }
    Write-Host "  待機中... ($i/10)" -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

# port-forward をバックグラウンドで起動
$logFile = Join-Path $env:TEMP "copilot-port-forward.log"
$pfJob = Start-Job -ScriptBlock {
    param($namespace, $service, $port, $logFile)
    kubectl port-forward -n $namespace svc/$service "${port}:${port}" *>&1 | Out-File -FilePath $logFile
} -ArgumentList "copilot-sdk", "gh-copilot", $LOCAL_PORT, $logFile

# 起動確認
Start-Sleep -Seconds 2
$jobState = (Get-Job -Id $pfJob.Id).State

if ($jobState -ne "Running") {
    Write-Error "Error: port-forward の起動に失敗しました。ログ: $logFile"
    exit 1
}

Write-Host "port-forward 起動中 (Job ID: $($pfJob.Id))。停止するには: Stop-Job -Id $($pfJob.Id); Remove-Job -Id $($pfJob.Id)" -ForegroundColor Green

# 環境変数をセット（現在のセッションに適用するにはドットソースで実行する必要があります）
$env:COPILOT_CLI_URL = "localhost:$LOCAL_PORT"
$env:COPILOT_PORT_FORWARD_JOB_ID = $pfJob.Id

Write-Host ""
Write-Host "環境変数をセットしました:" -ForegroundColor Green
Write-Host "  COPILOT_CLI_URL = $env:COPILOT_CLI_URL"
Write-Host "  COPILOT_PORT_FORWARD_JOB_ID = $env:COPILOT_PORT_FORWARD_JOB_ID"
Write-Host ""
Write-Host "注意: このスクリプトをドットソース (. k8s/set-url.ps1) で実行すると、" -ForegroundColor Yellow
Write-Host "      環境変数が現在のセッションに適用されます。" -ForegroundColor Yellow
