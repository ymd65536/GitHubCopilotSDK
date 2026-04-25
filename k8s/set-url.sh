#!/usr/bin/env bash
# gh-copilot Service へ kubectl port-forward を起動し、
# 環境変数 COPILOT_CLI_URL=localhost:4321 をセットするスクリプト
#
# 使い方:
#   eval "$(bash k8s/set-url.sh)"
#
# 注意: Rancher Desktop on macOS では LoadBalancer の EXTERNAL-IP に
#       ホストから直接アクセスできないため port-forward を使用します。

set -euo pipefail

LOCAL_PORT=4321

# 既存の port-forward プロセスを停止する
EXISTING_PID=$(pgrep -f "kubectl port-forward.*gh-copilot.*${LOCAL_PORT}" 2>/dev/null || true)
if [[ -n "${EXISTING_PID}" ]]; then
  kill "${EXISTING_PID}" 2>/dev/null || true
  echo "既存の port-forward (PID: ${EXISTING_PID}) を停止しました。" >&2
fi

# Pod が Running になるまで待つ
echo "Pod の起動を待機中..." >&2
for i in $(seq 1 10); do
  STATUS=$(kubectl get pods -n copilot-sdk -l app=copilot-sdk \
    -o jsonpath='{.items[0].status.phase}' 2>/dev/null || true)
  if [[ "${STATUS}" == "Running" ]]; then
    break
  fi
  echo "  待機中... (${i}/10)" >&2
  sleep 3
done

# port-forward をバックグラウンドで起動
kubectl port-forward -n copilot-sdk svc/gh-copilot ${LOCAL_PORT}:${LOCAL_PORT} \
  >/tmp/copilot-port-forward.log 2>&1 &
PF_PID=$!

# 起動確認
sleep 2
if ! kill -0 "${PF_PID}" 2>/dev/null; then
  echo "Error: port-forward の起動に失敗しました。ログ: /tmp/copilot-port-forward.log" >&2
  exit 1
fi

echo "port-forward 起動中 (PID: ${PF_PID})。停止するには: kill ${PF_PID}" >&2

# eval で読み込めるよう export 文を stdout に出力
echo "export COPILOT_CLI_URL=localhost:${LOCAL_PORT}"
echo "export COPILOT_PORT_FORWARD_PID=${PF_PID}"
