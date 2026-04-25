#!/bin/bash
# Kubernetes Pod内でinteractive_server.pyを実行するスクリプト

set -e

NAMESPACE="copilot-sdk"
POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app=copilot-sdk -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "Error: copilot-sdk Pod が見つかりません。"
    echo "kubectl get pods -n ${NAMESPACE} で確認してください。"
    exit 1
fi

echo "Pod名: ${POD_NAME}"
echo "スクリプトをPodにコピーしています..."

# スクリプトをPodにコピー
kubectl cp "$(dirname "$0")/interactive_server.py" \
    "${POD_NAME}:/tmp/interactive_server.py" -n "${NAMESPACE}"

echo "Pod内でスクリプトを実行します..."
echo "（終了するには 'exit' と入力してください）"
echo ""

# Pod内でスクリプトを実行（インタラクティブモード）
kubectl exec -it -n ${NAMESPACE} ${POD_NAME} -- \
    python3 /tmp/interactive_server.py

echo ""
echo "実行完了。"
