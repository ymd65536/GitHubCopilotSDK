# A2A Copilot - Test Script (PowerShell)

Write-Host "=== Testing A2A Copilot Deployment ===" -ForegroundColor Cyan

# Port forwardを起動（バックグラウンド）
Write-Host ">>> Starting port-forward to dispatcher service..." -ForegroundColor Yellow
$pfJob = Start-Job -ScriptBlock {
    kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot
}

# Port forwardの準備ができるまで待機
Start-Sleep -Seconds 5

# Cleanup function
function Cleanup {
    Write-Host ""
    Write-Host ">>> Stopping port-forward..." -ForegroundColor Yellow
    Stop-Job $pfJob -ErrorAction SilentlyContinue
    Remove-Job $pfJob -ErrorAction SilentlyContinue
}

try {
    $BASE_URL = "http://localhost:8000"

    Write-Host ""
    Write-Host "=== Test 1: Check dispatcher health ===" -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$BASE_URL/healthz" -Method Get
    $response | ConvertTo-Json
    Write-Host ""

    Write-Host ""
    Write-Host "=== Test 2: List registered agents ===" -ForegroundColor Cyan
    $agents = Invoke-RestMethod -Uri "$BASE_URL/agents" -Method Get
    $agents | ConvertTo-Json -Depth 5
    Write-Host ""

    Write-Host ""
    Write-Host "=== Test 3: Ask weather agent about Tokyo ===" -ForegroundColor Cyan
    $weatherRequest = @{
        capability = "weather"
        message = "What is the weather in Tokyo?"
    } | ConvertTo-Json
    
    $weatherResponse = Invoke-RestMethod -Uri "$BASE_URL/ask" -Method Post -Body $weatherRequest -ContentType "application/json"
    $weatherResponse | ConvertTo-Json
    Write-Host ""

    Write-Host ""
    Write-Host "=== Test 4: Ask calculator agent to calculate ===" -ForegroundColor Cyan
    $calcRequest = @{
        capability = "calculator"
        message = "Calculate 15 * 23 + 100"
    } | ConvertTo-Json
    
    $calcResponse = Invoke-RestMethod -Uri "$BASE_URL/ask" -Method Post -Body $calcRequest -ContentType "application/json"
    $calcResponse | ConvertTo-Json
    Write-Host ""

    Write-Host ""
    Write-Host "=== Test 5: Test currency conversion ===" -ForegroundColor Cyan
    $currencyRequest = @{
        capability = "calculator"
        message = "Convert 1000 USD to JPY"
    } | ConvertTo-Json
    
    $currencyResponse = Invoke-RestMethod -Uri "$BASE_URL/ask" -Method Post -Body $currencyRequest -ContentType "application/json"
    $currencyResponse | ConvertTo-Json
    Write-Host ""

    Write-Host ""
    Write-Host "✓ All tests completed!" -ForegroundColor Green
}
finally {
    Cleanup
}
