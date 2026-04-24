# GitHub Copilot SDK — Kubernetes ローカル実行ガイド

> **SDK更新に関する注意事項:**  
> GitHub Copilot Python SDK が更新され、API仕様が変更されました。現在の `interactive_server.py` は、ローカルの `copilot` CLI を直接起動する方式に対応しており、Kubernetes 上のサーバーへの直接的なTCP接続には対応していません。
> 
> 以下のKubernetesセットアップ手順（1〜7）は、コンテナ環境でサーバーを動かす参考情報として残していますが、Python クライアントからの接続方法については今後のSDKアップデートを待つ必要があります。

Rancher Desktop 上で GitHub Copilot サーバーをコンテナとして動かすためのマニフェスト一式です。

---

## ディレクトリ構成

```
k8s/
├── namespace.yaml            # Namespace: copilot-sdk
├── serviceaccount.yaml       # ServiceAccount
├── secret-provider-class.yaml# Secret の説明コメント（直接 apply 不要）
├── deployment.yaml           # Deployment（copilot --server --port 4321）
├── service.yaml              # LoadBalancer Service: gh-copilot (port 4321)
├── create-secret.sh          # GitHub トークンを Kubernetes Secret に登録（Bash版）
├── create-secret.ps1         # GitHub トークンを Kubernetes Secret に登録（PowerShell版）
├── set-url.sh                # port-forward 起動 + COPILOT_CLI_URL を環境変数にセット（Bash版）
├── set-url.ps1               # port-forward 起動 + COPILOT_CLI_URL を環境変数にセット（PowerShell版）
└── interactive_server.py     # Python クライアント（gh-copilot へ接続）
```

---

## 前提条件

### Kubernetes サーバーをセットアップする場合

| ツール | 用途 |
|---|---|
| [Rancher Desktop](https://rancherdesktop.io/) | ローカル Kubernetes + Docker ランタイム |
| [GitHub CLI (`gh`)](https://cli.github.com/) | トークン取得 |

### Python クライアントを実行する場合（推奨）

| ツール | 用途 |
|---|---|
| Python 3.10 以上 | スクリプト実行環境 |
| `copilot` パッケージ | `pip install copilot` でインストール |
| GitHub Copilot CLI | `npm install -g @githubnext/github-copilot-cli` または `gh copilot` |
| GitHub CLI (`gh`) | `gh auth login` で認証済み |

---

## セットアップ手順

> **注記:** 以下の手順1〜7は、Kubernetes上でcopilotサーバーをコンテナとして動かすためのものです。現在の `interactive_server.py` はローカルCLIを使用するため、これらの手順をスキップして直接セクション8に進むこともできます。

### 1. Rancher Desktop を起動する

Rancher Desktop を起動し、Kubernetes が有効になっていることを確認します。

```bash
# 例: Rancher Desktop を使う場合
kubectl config use-context rancher-desktop
kubectl get nodes
```

---

### 2. GitHub CLI にログインする

```bash
gh auth login
```

---

### 3. コンテナイメージをビルドする

```bash
docker build -t copilot-sdk:latest -f in_docker/Dockerfile .
```

> Rancher Desktop の Docker ランタイム（`docker:rancher-desktop`）を使用します。

---

### 4. Kubernetes Secret を作成する

`gh auth token` でトークンを取得し、Kubernetes Secret として登録します。
トークンはファイルに書かず、シェルセッション内のメモリのみで扱います。

**Bash版：**
```bash
bash k8s/create-secret.sh
```

**PowerShell版：**
```powershell
pwsh k8s/create-secret.ps1
```

`COPILOT_GITHUB_TOKEN` 環境変数が設定済みの場合は `gh auth token` の呼び出しをスキップします。

---

### 5. マニフェストを適用する

**Bash版：**
```bash
kubectl create namespace copilot-sdk
```

```bash
kubectl apply --validate=false \
  -f k8s/namespace.yaml \
  -f k8s/serviceaccount.yaml \
  -f k8s/deployment.yaml \
  -f k8s/service.yaml
```

**PowerShell版：**
```powershell
kubectl create namespace copilot-sdk
```

```powershell
kubectl apply --validate=false `
  -f k8s/namespace.yaml `
  -f k8s/serviceaccount.yaml `
  -f k8s/deployment.yaml `
  -f k8s/service.yaml
```

---

### 6. 起動確認

```bash
# Pod が Running になるまで待つ
kubectl get pods -n copilot-sdk

# サーバーログの確認
kubectl logs -n copilot-sdk deploy/copilot-sdk
# → "CLI server listening on port 4321" が出力されれば OK
```

---

### 7. 接続先 URL を環境変数にセットする

> **注意:** この手順は現在の `interactive_server.py` では使用されません（ローカルCLI起動のため）。Kubernetes サーバーに接続する将来のバージョン向けの参考情報として残しています。

`kubectl port-forward` をバックグラウンドで起動し、`COPILOT_CLI_URL=localhost:4321` を
シェルセッション限りの一時的な環境変数としてセットします。
シェルを閉じると環境変数は破棄されます。

> **Note:** Rancher Desktop on macOS/Windows では LoadBalancer の EXTERNAL-IP にホストから
> 直接アクセスできないため、`port-forward` 経由で `localhost:4321` を使用します。

**Bash版：**
```bash
eval "$(bash k8s/set-url.sh)"
```

**PowerShell版：**
```powershell
. k8s/set-url.ps1
```

**port-forward の停止方法：**

Bash版：
```bash
# eval で起動した場合（PID が環境変数に残っている）
kill $COPILOT_PORT_FORWARD_PID

# PID を忘れた場合・別シェルから停止する場合
pkill -f "kubectl port-forward.*gh-copilot"

# 動作確認
pgrep -a -f "kubectl port-forward"
```

PowerShell版：
```powershell
# Job ID が環境変数に残っている場合
Stop-Job -Id $env:COPILOT_PORT_FORWARD_JOB_ID
Remove-Job -Id $env:COPILOT_PORT_FORWARD_JOB_ID

# Job ID を忘れた場合・別シェルから停止する場合
Get-Job | Where-Object { $_.Command -like '*port-forward*' } | Stop-Job
Get-Job | Where-Object { $_.Command -like '*port-forward*' } | Remove-Job

# 動作確認
Get-Job
```

---

### 8. Python クライアントを実行する

> **注意:** 現在の `interactive_server.py` は更新されたSDKに対応するため、ローカルの `copilot` CLI を直接起動する方式に変更されています。Kubernetes 上のサーバーには接続しません。

#### 実行方法

```bash
python k8s/interactive_server.py
```

#### 出力例

```
Starting local copilot client...
🌤️  Weather Assistant (type 'exit' to quit)
   Try: 'What's the weather in Paris?' or 'Compare weather in NYC and LA'

You: What's the weather in Paris?
Assistant: It's currently **68°F** and **rainy** in Paris 🌧️. Don't forget an umbrella!

You: Compare weather in NYC and LA
Assistant: | City | Temp | Condition |
|------|------|-----------|
| 🗽 New York City | 60°F | Rainy 🌧️ |
| 🌴 Los Angeles | 63°F | Cloudy ☁️ |

LA is slightly warmer and drier — NYC is rainy while LA is just overcast today.

You: exit
```

> **動作確認済み:** カスタムツール（`get_weather`）が正常に呼び出され、ストリーミングレスポンスが動作しています。

#### SDK更新による主な変更点

最新のGitHub Copilot Python SDKでは以下の変更があります：

1. **CopilotClientの初期化**
   ```python
   # 旧（動作しない）
   client = CopilotClient({"cli_url": "localhost:4321"})
   
   # 新（ローカルCLIを起動）
   client = CopilotClient()
   ```

2. **create_sessionの引数**
   ```python
   # 旧（動作しない）
   session = await client.create_session({
       "streaming": True,
       "tools": [get_weather],
   })
   
   # 新（キーワード引数 + 必須パラメータ）
   session = await client.create_session(
       on_permission_request=PermissionHandler.approve_all,
       streaming=True,
       tools=[get_weather],
   )
   ```

3. **send_and_waitの引数**
   ```python
   # 旧（動作しない）
   await session.send_and_wait({"prompt": text})
   
   # 新（文字列を直接渡す）
   await session.send_and_wait(text)
   ```

4. **PermissionHandlerのインポート**
   ```python
   from copilot.session import PermissionHandler
   ```

#### Kubernetes サーバーに接続する場合

Kubernetes 上の copilot サーバーに接続したい場合は、GitHub Copilot Python SDK の最新仕様に従って `ExternalServerConfig` を使用する必要がありますが、現時点ではローカルプロセス起動を前提とした設計になっているため、直接的なTCP接続は非対応です。

代替案として、ローカルで `copilot` CLI を起動し、それを経由してリクエストを処理する現在の方式を推奨します。

---

## スクリプト詳細

### `create-secret.sh`

| 動作 | 説明 |
|---|---|
| `gh auth token` でトークン取得 | `COPILOT_GITHUB_TOKEN` が未設定の場合のみ実行 |
| `kubectl` コンテキスト解決 | `current-context` を優先。未設定時は `rancher-desktop` または先頭コンテキストへフォールバック |
| Namespace 作成 | `kubectl apply` で `copilot-sdk` を作成 |
| Secret 作成 | `--dry-run=client` パイプで冪等に apply |

### `set-url.sh`

`kubectl port-forward` をバックグラウンドで起動し、
`export COPILOT_CLI_URL=localhost:4321` を標準出力に出力します。
`eval` で現在のシェルに読み込みます。

Rancher Desktop on macOS では LoadBalancer の EXTERNAL-IP にホストから直接
アクセスできないため、この方式を採用しています。

---

## リソース削除

```bash
kubectl delete namespace copilot-sdk
```

Namespace ごと削除することで、Secret・Deployment・Service・ServiceAccount がすべて削除されます。

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| Pod が `InvalidImageName` | `docker images \| grep copilot-sdk` でイメージを確認し、`docker build` を再実行 |
| Pod が `CrashLoopBackOff` | `kubectl logs -n copilot-sdk deploy/copilot-sdk` でログを確認 |
| `EXTERNAL-IP` が `<pending>` | Rancher Desktop を再起動 |
| 接続タイムアウト | `eval "$(bash k8s/set-url.sh)"` を再実行して port-forward を再起動 |
| port-forward が切れた | `pkill -f "kubectl port-forward.*gh-copilot"` で停止後、`eval "$(bash k8s/set-url.sh)"` を再実行 |
| `COPILOT_PORT_FORWARD_PID` が未定義 | `pgrep -a -f "kubectl port-forward"` で PID を確認し `kill <PID>` で停止 |

---

## `kubectl` コンテキストが 0 件のとき

`kubectl config get-contexts` が空で、`kubectl cluster-info` が `localhost:8080` への接続エラーになる場合は、
`~/.kube/config` が未作成の可能性があります。

### 確認コマンド

```bash
kubectl config get-contexts
ls -la ~/.kube
```

`~/.kube/config` がない場合は、先にローカルクラスタを起動してコンテキストを作成します。

### 例: `minikube` でコンテキストを作成する

```bash
minikube start --driver=docker
kubectl config current-context
kubectl config get-contexts
```

期待される状態:

```text
current-context: minikube
contexts: minikube が 1 件以上表示される
```

その後、`create-secret.sh` を再実行します。

```bash
bash k8s/create-secret.sh
```

### `create-secret.sh` のコンテキスト選択ルール

`create-secret.sh` は以下の順で使用コンテキストを決定します。

1. `kubectl config current-context`（設定済みならそのまま使用）
2. `rancher-desktop`（`current-context` 未設定かつ存在する場合）
3. `kubectl config get-contexts -o name` の先頭

上記のいずれも取得できない場合は、コンテキスト未設定エラーで終了します。
