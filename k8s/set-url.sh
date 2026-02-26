#!/usr/bin/env bash
# gh-copilot Service の EXTERNAL-IP を取得して環境変数 COPILOT_CLI_URL をセットするスクリプト
#
# 使い方:
#   eval "$(bash k8s/set-url.sh)"

set -euo pipefail

EXTERNAL_IP=""
for i in $(seq 1 10); do
  EXTERNAL_IP=$(kubectl get svc gh-copilot -n copilot-sdk \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
  if [[ -n "${EXTERNAL_IP}" ]]; then
    break
  fi
  echo "  待機中... (${i}/10)" >&2
  sleep 3
done

if [[ -z "${EXTERNAL_IP}" ]]; then
  echo "Error: EXTERNAL-IP を取得できませんでした。Service の状態を確認してください。" >&2
  echo "  kubectl get svc -n copilot-sdk" >&2
  exit 1
fi

# eval で読み込めるよう export 文を stdout に出力
echo "export COPILOT_CLI_URL=${EXTERNAL_IP}:4321"
