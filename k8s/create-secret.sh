#!/usr/bin/env bash
# gh auth token で GitHub トークンを取得し、Kubernetes Secret を作成するスクリプト
#
# 使い方:
#   gh auth login   # 未ログインの場合のみ
#   bash k8s/create-secret.sh

set -euo pipefail

if ! command -v gh &>/dev/null; then
  echo "Error: gh コマンドが見つかりません。GitHub CLI をインストールしてください。" >&2
  exit 1
fi

# COPILOT_GITHUB_TOKEN が未定義の場合のみ gh auth token で取得する
if [[ -z "${COPILOT_GITHUB_TOKEN:-}" ]]; then
  COPILOT_GITHUB_TOKEN="$(gh auth token 2>/dev/null)"
  if [[ -z "${COPILOT_GITHUB_TOKEN}" ]]; then
    echo "Error: gh auth token の取得に失敗しました。先に 'gh auth login' を実行してください。" >&2
    exit 1
  fi
  echo "gh auth token からトークンを取得しました。"
else
  echo "環境変数 COPILOT_GITHUB_TOKEN が設定済みのため、gh auth token の取得をスキップします。"
fi

# ローカルクラスターのコンテキストに切り替える（rancher-desktop 前提）
LOCAL_CONTEXT="rancher-desktop"
CURRENT_CONTEXT="$(kubectl config current-context 2>/dev/null || true)"
echo "現在の kubectl コンテキスト: ${CURRENT_CONTEXT}"

if ! kubectl config get-contexts "${LOCAL_CONTEXT}" &>/dev/null; then
  echo "Error: コンテキスト '${LOCAL_CONTEXT}' が見つかりません。Rancher Desktop が起動しているか確認してください。" >&2
  exit 1
fi

if [[ "${CURRENT_CONTEXT}" != "${LOCAL_CONTEXT}" ]]; then
  kubectl config use-context "${LOCAL_CONTEXT}"
  echo "コンテキストを '${LOCAL_CONTEXT}' に切り替えました。"
fi

kubectl apply --validate=false -f "$(dirname "$0")/namespace.yaml"

# 既存の Secret を削除してから再作成（冪等性のため）
kubectl create secret generic copilot-sdk-secret \
  --namespace copilot-sdk \
  --from-literal=COPILOT_GITHUB_TOKEN="${COPILOT_GITHUB_TOKEN}" \
  --dry-run=client -o yaml | kubectl apply --validate=false -f -

echo "Secret 'copilot-sdk-secret' を namespace 'copilot-sdk' に作成しました。"
