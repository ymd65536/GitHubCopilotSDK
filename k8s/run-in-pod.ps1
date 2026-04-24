# Kubernetes Pod内でinteractive_server.pyを実行するスクリプト（PowerShell版）

$ErrorActionPreference = "Stop"

$NAMESPACE = "copilot-sdk"
$POD_NAME = (kubectl get pods -n $NAMESPACE -l app=copilot-sdk -o jsonpath='{.items[0].metadata.name}')

if (-not $POD_NAME) {
    Write-Error "Error: copilot-sdk Pod が見つかりません。`nkubectl get pods -n $NAMESPACE で確認してください。"
    exit 1
}

Write-Host "Pod名: $POD_NAME"
Write-Host "スクリプトをPodにコピーしています..."

# スクリプトをPodにコピー（相対パスを使用）
$originalLocation = Get-Location
Set-Location $PSScriptRoot
kubectl cp "interactive_server.py" "${POD_NAME}:/tmp/interactive_server.py" -n $NAMESPACE
Set-Location $originalLocation

Write-Host "Pod内でスクリプトを実行します..."
Write-Host "（終了するには 'exit' と入力してください）"
Write-Host ""

# Pod内でスクリプトを実行（インタラクティブモード）
kubectl exec -it -n $NAMESPACE $POD_NAME -- python3 /tmp/interactive_server.py

Write-Host ""
Write-Host "実行完了。"
