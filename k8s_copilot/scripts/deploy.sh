#!/bin/bash

# A2A Copilot - Kubernetes Deployment Script

set -e

echo "=== Deploying A2A Copilot to Kubernetes ==="

# 現在のディレクトリを保存
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo ""
echo "Project root: $PROJECT_ROOT"
echo ""

# Namespaceの作成
echo ">>> Creating namespace..."
kubectl apply -f "$PROJECT_ROOT/k8s/namespace.yaml"
echo ""

# GitHub Token Secretの確認
echo ">>> Checking GitHub token secret..."
if ! kubectl get secret github-token -n a2a-copilot &> /dev/null; then
    echo "⚠ GitHub token secret not found!"
    echo ""
    echo "Please create the secret with your GitHub token:"
    echo "  kubectl create secret generic github-token --from-literal=token=YOUR_TOKEN -n a2a-copilot"
    echo ""
    read -p "Press Enter after creating the secret, or Ctrl+C to cancel..."
fi
echo "✓ GitHub token secret exists"
echo ""

# Dispatcherのデプロイ
echo ">>> Deploying Dispatcher..."
kubectl apply -f "$PROJECT_ROOT/k8s/dispatcher.yaml"
echo ""

# Agentsのデプロイ
echo ">>> Deploying Weather Agent..."
kubectl apply -f "$PROJECT_ROOT/k8s/weather-agent.yaml"
echo ""

echo ">>> Deploying Calculator Agent..."
kubectl apply -f "$PROJECT_ROOT/k8s/calculator-agent.yaml"
echo ""

# デプロイメント状態の確認
echo "=== Deployment Status ==="
kubectl get all -n a2a-copilot
echo ""

# Podsの起動を待機
echo ">>> Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=dispatcher -n a2a-copilot --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=a2a-agent -n a2a-copilot --timeout=120s || true
echo ""

echo "✓ Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Check pod status: kubectl get pods -n a2a-copilot"
echo "  2. View dispatcher logs: kubectl logs -f -l app=dispatcher -n a2a-copilot"
echo "  3. Test the deployment: bash scripts/test-agents.sh"
echo "  4. Access dispatcher service: kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot"
