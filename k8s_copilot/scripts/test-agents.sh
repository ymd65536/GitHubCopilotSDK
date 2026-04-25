#!/bin/bash

# A2A Copilot - Test Script

set -e

echo "=== Testing A2A Copilot Deployment ==="

# Port forwardを起動（バックグラウンド）
echo ">>> Starting port-forward to dispatcher service..."
kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot &
PF_PID=$!

# Port forwardの準備ができるまで待機
sleep 5

# Cleanup function
cleanup() {
    echo ""
    echo ">>> Stopping port-forward..."
    kill $PF_PID 2>/dev/null || true
}

trap cleanup EXIT

BASE_URL="http://localhost:8000"

echo ""
echo "=== Test 1: Check dispatcher health ==="
curl -s "$BASE_URL/healthz" | python3 -m json.tool
echo ""

echo ""
echo "=== Test 2: List registered agents ==="
curl -s "$BASE_URL/agents" | python3 -m json.tool
echo ""

echo ""
echo "=== Test 3: Ask weather agent about Tokyo ==="
curl -s -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -d '{
        "capability": "weather",
        "message": "What is the weather in Tokyo?"
    }' | python3 -m json.tool
echo ""

echo ""
echo "=== Test 4: Ask calculator agent to calculate ==="
curl -s -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -d '{
        "capability": "calculator",
        "message": "Calculate 15 * 23 + 100"
    }' | python3 -m json.tool
echo ""

echo ""
echo "=== Test 5: Test currency conversion ==="
curl -s -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -d '{
        "capability": "calculator",
        "message": "Convert 1000 USD to JPY"
    }' | python3 -m json.tool
echo ""

echo ""
echo "✓ All tests completed!"
