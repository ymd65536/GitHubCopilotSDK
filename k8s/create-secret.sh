#!/usr/bin/env bash
# Kubernetes Secret を環境変数から生成するスクリプト
# 事前に環境変数 COPILOT_GITHUB_TOKEN をセットしてから実行してください。
#
# 使い方:
#   export COPILOT_GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
#   bash k8s/create-secret.sh

set -euo pipefail

if [[ -z "${COPILOT_GITHUB_TOKEN:-}" ]]; then
  echo "Error: 環境変数 COPILOT_GITHUB_TOKEN が設定されていません。" >&2
  echo "  export COPILOT_GITHUB_TOKEN=\"ghp_xxxxxxxxxxxx\"" >&2
  exit 1
fi

kubectl apply -f "$(dirname "$0")/namespace.yaml"

# 既存の Secret を削除してから再作成（冪等性のため）
kubectl create secret generic copilot-sdk-secret \
  --namespace copilot-sdk \
  --from-literal=COPILOT_GITHUB_TOKEN="${COPILOT_GITHUB_TOKEN}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secret 'copilot-sdk-secret' を namespace 'copilot-sdk' に作成しました。"
