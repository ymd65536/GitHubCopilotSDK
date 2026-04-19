#!/usr/bin/env pwsh
# gh auth token で GitHub トークンを取得し、Kubernetes Secret を作成するスクリプト
#
# 使い方:
#   gh auth login   # 未ログインの場合のみ
#   pwsh k8s/create-secret.ps1

$ErrorActionPreference = 'Stop'

# gh コマンドの存在確認
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "Error: gh コマンドが見つかりません。GitHub CLI をインストールしてください。"
    exit 1
}

# COPILOT_GITHUB_TOKEN が未定義の場合のみ gh auth token で取得する
if (-not $env:COPILOT_GITHUB_TOKEN) {
    try {
        $env:COPILOT_GITHUB_TOKEN = gh auth token 2>$null
        if (-not $env:COPILOT_GITHUB_TOKEN) {
            Write-Error "Error: gh auth token の取得に失敗しました。先に 'gh auth login' を実行してください。"
            exit 1
        }
        Write-Host "gh auth token からトークンを取得しました。"
    }
    catch {
        Write-Error "Error: gh auth token の取得に失敗しました。先に 'gh auth login' を実行してください。"
        exit 1
    }
}
else {
    Write-Host "環境変数 COPILOT_GITHUB_TOKEN が設定済みのため、gh auth token の取得をスキップします。"
}

# 現在の kubectl コンテキストを優先し、未設定時のみフォールバックする
$PREFERRED_FALLBACK_CONTEXT = "rancher-desktop"
$CURRENT_CONTEXT = kubectl config current-context 2>$null

if ($CURRENT_CONTEXT) {
    $TARGET_CONTEXT = $CURRENT_CONTEXT
    Write-Host "現在の kubectl コンテキストを使用します: $TARGET_CONTEXT"
}
else {
    # フォールバックコンテキストの存在確認
    $contextExists = kubectl config get-contexts $PREFERRED_FALLBACK_CONTEXT 2>$null
    if ($contextExists) {
        $TARGET_CONTEXT = $PREFERRED_FALLBACK_CONTEXT
    }
    else {
        $TARGET_CONTEXT = (kubectl config get-contexts -o name 2>$null | Select-Object -First 1)
    }

    if (-not $TARGET_CONTEXT) {
        Write-Error "Error: kubectl のコンテキストが1つも設定されていません。'kubectl config get-contexts' で確認し、先にコンテキストを作成/設定してください。"
        exit 1
    }

    kubectl config use-context $TARGET_CONTEXT >$null
    Write-Host "current-context が未設定のため '$TARGET_CONTEXT' を選択しました。"
}

# スクリプトのディレクトリパスを取得
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# namespace の作成
kubectl apply --validate=false -f "$scriptDir/namespace.yaml"

# 既存の Secret を削除してから再作成（冪等性のため）
kubectl create secret generic copilot-sdk-secret `
    --namespace copilot-sdk `
    --from-literal=COPILOT_GITHUB_TOKEN="$env:COPILOT_GITHUB_TOKEN" `
    --dry-run=client -o yaml | kubectl apply --validate=false -f -

Write-Host "Secret 'copilot-sdk-secret' を namespace 'copilot-sdk' に作成しました。"
