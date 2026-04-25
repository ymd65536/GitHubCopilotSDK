# GitHub Copilot SDK — Agent-to-Agent (A2A) 構成

このフォルダでは、複数のCopilotサーバーが相互に接続するAgent-to-Agent (A2A) アーキテクチャを実装します。

## アーキテクチャ概要

```
┌─────────────────┐
│   Dispatcher    │  ← クライアントからのリクエストを受信
│   (Port 8000)   │     能力ベースでエージェントにルーティング
└────────┬────────┘
         │
         ├─────────────┬─────────────┐
         ▼             ▼             │
    ┌─────────┐  ┌──────────┐      │
    │ Weather │  │Calculator│      │ (未実装エージェント)
    │  Agent  │  │  Agent   │      │
    │✅ 実装済 │  │✅ 実装済  │      │
    │(Port8001)│  │(Port8002)│      │
    └─────────┘  └──────────┘      │
    get_weather   calculate +       │
                 convert_currency    ▼
                                将来拡張可能
                                (File Ops, Translation等)
```

**実装済みエージェント**: 2個（Weather, Calculator）  
**動作確認済み機能**: ✅ 完全動作  
**GitHub Copilot SDK**: v0.2.2 使用

## 特徴

- **自動エージェント検出**: Kubernetes上の各Podが`app=a2a-agent`ラベルで自動検出される
- **能力ベースルーティング**: 各エージェントが公開する`agent-card.json`に基づいてリクエストをルーティング
- **独立したツールセット**: 各エージェントは独自のカスタムツールを持つ
- **スケーラブル**: 新しいエージェントを追加するには、ラベルを付けてデプロイするだけ

## 実装状況

### ✅ 実装済みエージェント

#### 1. Weather Agent (天気エージェント)
**能力**: `weather`  
**ステータス**: ✅ 実装完了・動作確認済み  
**ツール**:
- `get_weather(city)`: 都市の天気情報を取得（モックデータ使用）

**動作例**:
```bash
# リクエスト
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"capability": "weather", "message": "What is the weather in Tokyo?"}'

# レスポンス
{
  "agent": "Weather Agent",
  "endpoint": "http://weather-agent-svc:8001",
  "response": "The current weather in **Tokyo** is:\n- 🌡️ **Temperature:** 18°C\n- ☁️ **Condition:** Cloudy"
}
```

#### 2. Calculator Agent (計算エージェント)  
**能力**: `calculator`  
**ステータス**: ✅ 実装完了・動作確認済み  
**ツール**:
- `calculate(expression)`: 数式を計算
- `convert_currency(amount, from_currency, to_currency)`: 通貨換算（モック為替レート使用）

**動作例**:
```bash
# 計算リクエスト
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"capability": "calculator", "message": "Calculate 15 * 23 + 100"}'

# レスポンス
{
  "agent": "Calculator Agent",
  "endpoint": "http://calculator-agent-svc:8002",
  "response": "**15 * 23 + 100 = 445**\n\nBreakdown:\n- 15 × 23 = 345\n- 345 + 100 = **445**"
}

# 通貨換算リクエスト
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"capability": "calculator", "message": "Convert 1000 USD to JPY"}'

# レスポンス
{
  "agent": "Calculator Agent",
  "endpoint": "http://calculator-agent-svc:8002",
  "response": "**1,000 USD = 110,000 JPY**\n\nExchange rate used: **1 USD = 110 JPY**"
}
```

### 📋 未実装エージェント（将来実装予定）

#### 3. File Operations Agent (ファイル操作エージェント)
**能力**: `file_operations`  
**ステータス**: 未実装  
**ツール**:
- `read_file(path)`: ファイルを読み込む
- `write_file(path, content)`: ファイルに書き込む
- `list_directory(path)`: ディレクトリの内容を一覧表示

#### 4. Translation Agent (翻訳エージェント)
**能力**: `translation`  
**ステータス**: 未実装  
**ツール**:
- `translate(text, target_language)`: テキストを翻訳
- `detect_language(text)`: 言語を検出

## ディレクトリ構成

```
k8s_copilot/
├── README.md                     # このファイル
├── dispatcher/
│   ├── dispatcher.py             # ✅ Dispatcherサービス（実装済み）
│   ├── Dockerfile                # ✅ Dispatcherイメージ（実装済み）
│   └── requirements.txt          # ✅ Python依存関係（実装済み）
├── agents/
│   ├── weather_agent.py          # ✅ 天気エージェント（実装済み）
│   ├── calculator_agent.py       # ✅ 計算エージェント（実装済み）
│   ├── Dockerfile                # ✅ エージェント共通イメージ（実装済み）
│   └── requirements.txt          # ✅ Python依存関係（実装済み）
├── k8s/
│   ├── namespace.yaml            # ✅ Namespace定義（実装済み）
│   ├── dispatcher.yaml           # ✅ Dispatcherデプロイメント（実装済み）
│   ├── weather-agent.yaml        # ✅ 天気エージェントデプロイメント（実装済み）
│   └── calculator-agent.yaml     # ✅ 計算エージェントデプロイメント（実装済み）
└── scripts/
    ├── build-images.sh           # ✅ イメージビルドスクリプト（実装済み）
    ├── build-images.ps1          # ✅ PowerShellビルドスクリプト（実装済み）
    ├── deploy.sh                 # ✅ デプロイスクリプト（実装済み）
    ├── deploy.ps1                # ✅ PowerShellデプロイスクリプト（実装済み）
    ├── test-agents.sh            # ✅ テストスクリプト（実装済み）
    └── test-agents.ps1           # ✅ PowerShellテストスクリプト（実装済み）
```

## セットアップ手順

### 0. GitHub認証

GitHub Copilot SDKを使用するには、GitHub認証が必要です。

#### GitHub CLIで認証（推奨）

GitHub CLIを使用すると、トークンが自動的に管理されます：

```bash
gh auth login
```

対話形式で以下を選択：
1. **What account do you want to log into?** → `GitHub.com`
2. **What is your preferred protocol for Git operations?** → `HTTPS` または `SSH`
3. **Authenticate Git with your GitHub credentials?** → `Yes`
4. **How would you like to authenticate GitHub CLI?** → `Login with a web browser` （推奨）

ブラウザでGitHubにログインすると、認証が完了します。

認証後、トークンを取得：

```bash
gh auth token
```

このトークンを次の手順でKubernetes Secretに設定します。

#### 手動でトークンを作成する方法

GitHub CLIが使えない場合は、手動でPersonal Access Tokenを作成できます：

1. https://github.com/settings/tokens にアクセス
2. **Generate new token (classic)** をクリック
3. スコープで `copilot` と `read:user` を選択
4. 生成されたトークン（`ghp_...`）をコピー

### 1. イメージのビルド

```bash
cd k8s_copilot
bash scripts/build-images.sh
```

または PowerShell の場合：

```powershell
cd k8s_copilot
.\scripts\build-images.ps1
```

### 2. Namespaceの作成

まず、Kubernetes上にnamespaceを作成します：

```bash
kubectl apply -f k8s/namespace.yaml
```

### 3. GitHubトークンのSecretを作成

手順0で取得したトークンを使用して、Kubernetes Secretを作成します：

```bash
# GitHub CLIを使用した場合
kubectl create secret generic github-token \
  --from-literal=token=$(gh auth token) \
  -n a2a-copilot
```

手動で作成する場合：

```bash
kubectl create secret generic github-token \
  --from-literal=token=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  -n a2a-copilot
```

### 3.1. Copilotモデルの指定（任意）

Copilot CLI/SDK が使用するモデルは、環境変数 `COPILOT_MODEL` で指定できます。

このA2A構成では、各Deployment（Dispatcher / Weather Agent / Calculator Agent）に以下を設定しています：

```text
COPILOT_MODEL=gpt-5-mini
```

別のモデルを使いたい場合は、以下のマニフェストの `env:` を変更して再デプロイしてください。

- `k8s/dispatcher.yaml`
- `k8s/weather-agent.yaml`
- `k8s/calculator-agent.yaml`

PowerShell の場合：

```powershell
# GitHub CLIを使用した場合
kubectl create secret generic github-token `
  --from-literal=token=$(gh auth token) `
  -n a2a-copilot

# 手動で作成する場合
kubectl create secret generic github-token `
  --from-literal=token=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx `
  -n a2a-copilot
```

### 4. エージェントのデプロイ

```bash
kubectl apply -f k8s/
```

または、デプロイスクリプトを使用：

```bash
# Bash
bash scripts/deploy.sh
```

```powershell
# PowerShell
.\scripts\deploy.ps1
```

**注意**: デプロイスクリプトはnamespace作成とSecret作成も含むため、手順2-3を実行済みの場合はこのスクリプトだけで完了します。

### 5. 動作確認

#### Podの状態を確認

```bash
kubectl get pods -n a2a-copilot
```

すべてのPodが `Running` 状態になるまで待ちます。

#### Dispatcherサービスへのアクセス

Port forwardでローカルからアクセスできるようにします：

```bash
kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot
```

別のターミナルでエージェント一覧を取得：

```bash
curl http://localhost:8000/agents
```

#### テストスクリプトの実行

自動テストスクリプトを実行して、すべてのエージェントが正常に動作するか確認します：

```bash
# Bash
bash scripts/test-agents.sh
```

```powershell
# PowerShell
.\scripts\test-agents.ps1
```

### 6. エージェントへのリクエスト

天気情報を取得：

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "weather",
    "message": "What is the weather in Tokyo?"
  }'
```

計算を実行：

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "calculator",
    "message": "Calculate 15 * 23 + 100"
  }'
```

PowerShellの場合：

```powershell
# 天気情報を取得
$response = Invoke-RestMethod -Uri http://localhost:8000/ask `
  -Method Post `
  -Body (@{capability='weather'; message='What is the weather in Tokyo?'} | ConvertTo-Json) `
  -ContentType 'application/json'
$response.response

# 計算を実行
$response = Invoke-RestMethod -Uri http://localhost:8000/ask `
  -Method Post `
  -Body (@{capability='calculator'; message='Calculate 15 * 23 + 100'} | ConvertTo-Json) `
  -ContentType 'application/json'
$response.response

# 通貨換算
$response = Invoke-RestMethod -Uri http://localhost:8000/ask `
  -Method Post `
  -Body (@{capability='calculator'; message='Convert 1000 USD to JPY'} | ConvertTo-Json) `
  -ContentType 'application/json'
$response.response
```

## Agent Cardの仕様

各エージェントは`.well-known/agent-card.json`エンドポイントで以下の情報を公開します：

```json
{
  "name": "Weather Agent",
  "description": "Provides weather information for cities worldwide",
  "capabilities": {
    "extensions": [
      {
        "name": "weather",
        "description": "Get weather information"
      }
    ]
  },
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather for a city",
      "parameters": {
        "city": {
          "type": "string",
          "description": "City name"
        }
      }
    }
  ]
}
```

## テスト結果

全自動テストが正常に完了しています：

```bash
✓ Test 1: Dispatcher health check - OK (2 agents registered)
✓ Test 2: List registered agents - OK (Weather Agent, Calculator Agent)
✓ Test 3: Weather query (Tokyo) - OK
✓ Test 4: Calculator (15 * 23 + 100) - OK (Result: 445)
✓ Test 5: Currency conversion (1000 USD to JPY) - OK (Result: 110,000 JPY)
```

### 動作確認済み機能

- ✅ Dispatcher起動とヘルスチェック
- ✅ エージェント自動検出（Agent Card経由）
- ✅ 能力ベースルーティング
- ✅ Weather Agent - 天気情報取得
- ✅ Calculator Agent - 数式計算
- ✅ Calculator Agent - 通貨換算
- ✅ GitHub Copilot SDKカスタムツール統合
- ✅ Kubernetes上での複数エージェント連携

## トラブルシューティング

### 1. Podが起動しない

**症状**: Pod が `ImagePullBackOff` または `ErrImagePull` 状態

**解決方法**:
```bash
# イメージがローカルに存在するか確認
docker images | grep a2a

# イメージを再ビルド
cd k8s_copilot
bash scripts/build-images.sh  # または .\scripts\build-images.ps1
```

### 2. エージェントが登録されない

**症状**: `curl http://localhost:8000/agents` が空のリストを返す

**原因と解決方法**:

#### 原因1: GitHubトークンが無効
```bash
# Secretを確認
kubectl get secret github-token -n a2a-copilot

# トークンを再作成
kubectl delete secret github-token -n a2a-copilot
kubectl create secret generic github-token --from-literal=token=$(gh auth token) -n a2a-copilot

# Podを再起動
kubectl rollout restart deployment -n a2a-copilot
```

#### 原因2: エージェントPodがまだ起動中
```bash
# Pod状態を確認
kubectl get pods -n a2a-copilot

# すべてのPodが Running になるまで待機
kubectl wait --for=condition=ready pod -l app=a2a-agent -n a2a-copilot --timeout=120s
```

#### 原因3: ツール定義のエラー
```bash
# エージェントログを確認
kubectl logs -l agent=weather -n a2a-copilot
kubectl logs -l agent=calculator -n a2a-copilot

# エラーがある場合は、エージェントコードを修正してイメージを再ビルド
```

### 3. ツール定義のベストプラクティス

GitHub Copilot SDK v0.2.2 以降では、ツール定義に以下の形式が必要です：

```python
from pydantic import BaseModel, Field
from github_copilot_sdk import define_tool

# ✅ 正しい方法
class WeatherParams(BaseModel):
    city: str = Field(description="City name")

@define_tool(description="Get current weather information for a city")
async def get_weather(params: WeatherParams) -> dict:
    return {"city": params.city, "temperature": "20°C"}

# ❌ 間違った方法（古いバージョンの書き方）
@define_tool
def get_weather(city: str):
    return {"city": city, "temperature": "20°C"}
```

**重要ポイント**:
- ✅ `@define_tool(description="...")` でdescriptionを指定
- ✅ `async def` を使用（非同期関数）
- ✅ Pydantic `BaseModel` でパラメータを定義
- ✅ `dict` を返す
- ❌ 通常の関数引数は使用不可
- ❌ 同期関数（`def`）は使用不可

### 4. Namespace関連エラー

**症状**: `namespaces "a2a-copilot" not found`

**解決方法**:
```bash
# Namespaceを先に作成
kubectl apply -f k8s/namespace.yaml

# その後Secretを作成
kubectl create secret generic github-token \
  --from-literal=token=$(gh auth token) \
  -n a2a-copilot
```

**注意**: Namespaceを作成する前にSecretやDeploymentを作成するとエラーになります。

### 5. Port Forwardが切断される

**症状**: `curl` コマンドが `Connection refused` を返す

**解決方法**:
```bash
# Port forwardを再実行
kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot

# またはバックグラウンドで実行
kubectl port-forward svc/dispatcher-svc 8000:8000 -n a2a-copilot &
```

### 6. レスポンス処理エラー

**症状**: `'async for' requires an object with __aiter__ method, got coroutine`

**原因**: `send()` メソッドを直接イテレートしようとした

**解決方法**:
```python
# ❌ 間違った方法
async for event in copilot_session.send(message):
    response_text += event.delta

# ✅ 正しい方法
response = await copilot_session.send_and_wait(message)
response_text = response.data.content
```

## 技術仕様

### GitHub Copilot SDK
- **バージョン**: 0.2.2以降
- **主要変更**: `@define_tool` がPydantic BaseModelベースのパラメータを要求
- **セッション管理**: 各エージェントが独自の `CopilotSession` を持つ
- **レスポンス処理**: `send_and_wait()` を使用してSessionEventオブジェクトを取得

### Kubernetes
- **Namespace**: `a2a-copilot`
- **ラベル**: 
  - Dispatcher: `app=dispatcher`
  - Agents: `app=a2a-agent`, `agent=<agent-name>`
- **サービスタイプ**:
  - Dispatcher: `LoadBalancer` (外部アクセス用)
  - Agents: `ClusterIP` (内部通信のみ)

### Docker
- **ベースイメージ**:
  - Dispatcher: `python:3.11-slim`
  - Agents: `debian:bookworm` (GitHub CLI + Node.js + Copilot CLI含む)
- **イメージプル**: `imagePullPolicy: Never` (Rancher Desktopでローカルイメージ使用)

## 参考リンク

- [A2ADemo Repository](https://github.com/ymd65536/A2ADemo)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [GitHub Copilot Python SDK](https://pypi.org/project/github-copilot-sdk/)
- [GitHub Copilot SDK v0.2.2 変更点](https://github.com/copilot-extensions/preview-sdk.python/releases)
