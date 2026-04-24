#!/bin/bash

# A2A Copilot - Docker Image Build Script

set -e

echo "=== Building A2A Copilot Docker Images ==="

# 現在のディレクトリを保存
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo ""
echo "Project root: $PROJECT_ROOT"
echo ""

# Dispatcher イメージのビルド
echo ">>> Building Dispatcher image..."
cd "$PROJECT_ROOT/dispatcher"
docker build -t a2a-dispatcher:latest .
echo "✓ Dispatcher image built successfully"
echo ""

# Agent イメージのビルド
echo ">>> Building Agent image..."
cd "$PROJECT_ROOT/agents"
docker build -t a2a-agent:latest .
echo "✓ Agent image built successfully"
echo ""

# イメージ一覧を表示
echo "=== Built Images ==="
docker images | grep a2a-
echo ""

echo "✓ All images built successfully!"
echo ""
echo "Next steps:"
echo "  1. Create GitHub token secret: kubectl create secret generic github-token --from-literal=token=YOUR_TOKEN -n a2a-copilot"
echo "  2. Deploy to Kubernetes: bash scripts/deploy.sh"
