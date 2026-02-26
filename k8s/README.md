# GitHub Copilot SDK — Kubernetes ローカル実行ガイド

Rancher Desktop 上で GitHub Copilot サーバーをコンテナとして動かし、
Python クライアント (`interactive_server.py`) から接続するためのマニフェスト一式です。

---

## ディレクトリ構成

```
k8s/
├── namespace.yaml            # Namespace: copilot-sdk
├── serviceaccount.yaml       # ServiceAccount
├── secret-provider-class.yaml# Secret の説明コメント（直接 apply 不要）
├── deployment.yaml           # Deployment（copilot --server --port 4321）
├── service.yaml              # LoadBalancer Service: gh-copilot (port 4321)
├── create-secret.sh          # GitHub トークンを Kubernetes Secret に登録
├── set-url.sh                # Service の EXTERNAL-IP を環境変数にセット
└── interactive_server.py     # Python クライアント（gh-copilot へ接続）
```

---

## 前提条件

| ツール | 用途 |
|---|---|
| [Rancher Desktop](https://rancherdesktop.io/) | ローカル Kubernetes + Docker ランタイム |
| [GitHub CLI (`gh`)](https://cli.github.com/) | トークン取得 |
| Python 3.10 以上 + `copilot` パッケージ | クライアント実行 |

---

## セットアップ手順

### 1. Rancher Desktop を起動する

Rancher Desktop を起動し、Kubernetes が有効になっていることを確認します。

```bash
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

```bash
bash k8s/create-secret.sh
```

`COPILOT_GITHUB_TOKEN` 環境変数が設定済みの場合は `gh auth token` の呼び出しをスキップします。

---

### 5. マニフェストを適用する

```bash
kubectl apply --validate=false \
  -f k8s/serviceaccount.yaml \
  -f k8s/deployment.yaml \
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

# Service の EXTERNAL-IP を確認
kubectl get svc -n copilot-sdk
```

---

### 7. 接続先 URL を環境変数にセットする

```bash
eval "$(bash k8s/set-url.sh)"
```

`COPILOT_CLI_URL` がシェルセッション限りの一時的な環境変数としてセットされます。
シェルを閉じると自動的に破棄されます（ファイルへの書き込みは行いません）。

---

### 8. Python クライアントを実行する

```bash
python k8s/interactive_server.py
```

```
Connecting to gh-copilot service at 192.168.x.x:4321 ...
🌤️  Weather Assistant (type 'exit' to quit)
   Try: 'What's the weather in Paris?' or 'Compare weather in NYC and LA'

You:
```

---

## スクリプト詳細

### `create-secret.sh`

| 動作 | 説明 |
|---|---|
| `gh auth token` でトークン取得 | `COPILOT_GITHUB_TOKEN` が未設定の場合のみ実行 |
| `rancher-desktop` コンテキストへ切り替え | 別コンテキストの場合は自動切り替え |
| Namespace 作成 | `kubectl apply` で `copilot-sdk` を作成 |
| Secret 作成 | `--dry-run=client` パイプで冪等に apply |

### `set-url.sh`

`kubectl get svc gh-copilot` の EXTERNAL-IP を取得し、
`export COPILOT_CLI_URL=<IP>:4321` を標準出力に出力します。
`eval` で現在のシェルに読み込みます。

---

## リソース削除

```bash
kubectl delete namespace copilot-sdk
```

Namespace ごと削除することで、Secret・Deployment・Service・ServiceAccount がすべて削除されます。

---

## トラブルシューティング

| 症状 | 確認コマンド |
|---|---|
| Pod が `InvalidImageName` | `docker images \| grep copilot-sdk` でイメージ確認 |
| Pod が `CrashLoopBackOff` | `kubectl logs -n copilot-sdk deploy/copilot-sdk` |
| `EXTERNAL-IP` が `<pending>` | Rancher Desktop の再起動 |
| 接続タイムアウト | `kubectl get svc -n copilot-sdk` で IP を再確認し `eval "$(bash k8s/set-url.sh)"` を再実行 |
