# GitHub Copilot SDK Sample

## Overview

ここから触る。[copilot-sdk](https://github.com/github/copilot-sdk)
セットアップは大変なのでCodepacesで始めます。

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ymd65536/GitHubCopilotSDK)

ちなみに手動でセットアップする場合に必要なものは以下の通りです。

- Copilot CLI
- 各ランタイムで利用できるGitHub Copilot SDK
  - github-copilot-sdk

おまけですが、GitHub CLIも入れておくと便利です。

## Getting Started

[getting-started.md](https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md)を参考に進めてみよう。

```bash
copilot --version
# 0.0.395
# Commit: 4b4fe6e
```

## 最初のメッセージ送信

まずはメッセージを送信してみます。

```python
python python/your_first_message.py
```

実行結果

```text
2 + 2 = 4 です。
```

まずはこれが動けばOKです。
しかし、メッセージが届くまでに時間がかかる場合があります。それまでターミナルを見つめないといけません。
そこで、メッセージを少しずつ流してくれるストリーミングの方法を試してみます。

## ストリーミングでメッセージ送信

ストリーミングでメッセージを送信するには以下のようにします。

```python
python python/streaming_response.py
```

これでメッセージが少しずつ流れてくるようになります。

## ツールを使う

次はツールを使ってみます。ツール呼び出しを使うと、外部のAPIやデータベースにアクセスして情報を取得したり、操作を実行したりできます。

```python
python python/custom_tool.py
```

実行結果

```text
シアトルは晴れで気温は51°F、東京も晴れで気温は65°Fです。どちらも晴れですが、東京の方が暖かいです。
```

## 対話のはじまり！！！

次は諦めずにCopilotとの対話を続けてみます。

```python
python python/interactive.py
```

実行すると、対話モードに入って、Copilotと連続してメッセージをやり取りできます。

## サーバーモードを使うんだ！！

サーバーモードを使うと、CopilotクライアントがアクセスするURLを指定できます。
これにより、ローカルでホストされているカスタムサーバーやプロキシサーバーを利用できます。

まずはサーバーを起動します。

```bash
copilot --server --port 4321
```

別のターミナルでクライアントを起動します。

```python
python python/server_mode.py
```

ポイントは`cli_url`を指定することです。

```python
async def main():
    client = CopilotClient({
        "cli_url": "localhost:4321"
    })
    await client.start()
```

## サーバーモードで対話の始まり！！

では、これまでの応用で対話をサーバーモードで試してみます。

まずはサーバーを起動します。

```bash
copilot --server --port 4321
```

別のターミナルでクライアントを起動します。

```python
python python/interactive_server.py
```

これでサーバーモードで対話が始まります。（対話の始まり！！！）

## dockerで動かす

```bash
cd in_docker
```

```bash
docker build -t copilot-server .
docker run -p 4321:4321 -it --rm copilot-sdk /bin/bash
```

```bash
gh auth login
```

```bash
export COPILOT_MODEL=gemini-3-pro-preview
```

```bash
copilot -i "Hello, world!"
```

```bash
copilot help config
```

```bash
copilot --server --port 4321
```

## Kubernetesで動かす

KubernetesクラスタでGitHub Copilot SDKを実行できます。詳細は [k8s/README.md](k8s/README.md) を参照してください。

### クイックスタート

1. **イメージのビルド**

```bash
cd in_docker
docker build -t copilot-sdk:latest .
```

2. **GitHubトークンのシークレット作成**

```bash
kubectl create secret generic github-token \
  --from-literal=token=YOUR_GITHUB_TOKEN \
  -n copilot-sdk
```

3. **デプロイ**

```bash
cd ../k8s
kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

4. **Pod内でスクリプトを実行**

```powershell
# PowerShell
.\k8s\run-in-pod.ps1
```

```bash
# Bash
bash k8s/run-in-pod.sh
```

### Agent-to-Agent (A2A) アーキテクチャ

複数のCopilotエージェントが相互に連携するA2A構成については、[k8s_copilot/README.md](k8s_copilot/README.md) を参照してください。

この構成では、各エージェントが独自のツールセットを持ち、Dispatcherが能力に基づいてリクエストをルーティングします。

## GitHub Copilot SDK v0.2.2 への移行

GitHub Copilot Python SDKは**v0.2.2で大きなAPI変更**がありました。

### 主な変更点

| 項目 | 旧API (v0.1.x) | 新API (v0.2.x) |
|------|----------------|----------------|
| **クライアント初期化** | `CopilotClient({"cli_url": "..."})` | `CopilotClient()` (引数なし) |
| **セッション作成** | `await client.create_session({"streaming": True, ...})` | `await client.create_session(streaming=True, on_permission_request=PermissionHandler.approve_all, ...)` |
| **メッセージ送信** | `await session.send_and_wait({"content": message})` | `await session.send_and_wait(message)` (文字列を直接渡す) |
| **PermissionHandler** | `from copilot import PermissionHandler` | `from copilot.session import PermissionHandler` |
| **必須パラメータ** | なし | `on_permission_request` が必須 |
| **パッケージ名** | `copilot` (Flask関連パッケージと衝突) | `github-copilot-sdk` (正式パッケージ) |

### 移行例

**旧コード (v0.1.x):**
```python
from copilot import CopilotClient, PermissionHandler

client = CopilotClient({"cli_url": "localhost:4321"})
session = await client.create_session({
    "streaming": True,
    "tools": [get_weather]
})
await session.send_and_wait({"content": "Hello"})
```

**新コード (v0.2.x):**
```python
from copilot import CopilotClient
from copilot.session import PermissionHandler  # インポート元変更
from copilot.tools import define_tool

client = CopilotClient()  # 引数なし
session = await client.create_session(
    on_permission_request=PermissionHandler.approve_all,  # 必須
    streaming=True,
    tools=[get_weather],
)
await session.send_and_wait("Hello")  # 文字列を直接渡す
```

### 注意点

- **`ExternalServerConfig` は非推奨**: 外部サーバーを指定しても、内部的にローカルCLIが必要なため、Pod内で実行する方が確実です
- **`on_permission_request` は必須**: ツールを使う場合は必ず指定してください（`PermissionHandler.approve_all` が推奨）
- **パッケージ名に注意**: PyPIの `copilot` パッケージはFlask関連で別物です。`github-copilot-sdk` を使用してください

## Copilot CLI Configuration Settings

GitHub Copilot CLIの設定項目を以下にまとめます。

| 項目名 | 説明 | デフォルト値 | 補足・選択肢 |
| :--- | :--- | :--- | :--- |
| `allowed_urls` | プロンプトなしでアクセスを許可するURL/ドメインのリスト。 | - | 完全一致、ドメイン指定、ワイルドカード（`*.github.com`）に対応。 |
| `auto_update` | CLIの自動アップデートを有効にするか。 | `true` | - |
| `banner` | アニメーションバナーを表示する頻度。 | `"once"` | `always`, `never`, `once` |
| `beep` | ユーザーの注意が必要な際にビープ音を鳴らすか。 | `true` | - |
| `compact_paste` | 長い貼り付け内容をコンパクトなトークンに折り畳むか。 | `true` | `true`の場合、10行以上は `[Paste #N - X lines]` と表示。 |
| `custom_agents.default_local_only` | ローカルのカスタムエージェントのみを使用するか。 | `false` | - |
| `denied_urls` | アクセスを拒否するURL/ドメインのリスト。 | - | **許可ルールよりも優先されます。** |
| `experimental` | 実験的な機能を有効にするか。 | `false` | フラグや `/experimental` コマンドで変更可能。 |
| `launch_messages` | 起動時に表示するメッセージのリスト。 | - | 起動時にランダムに1つ表示。チーム用のお知らせなどに。 |
| `log_level` | CLIのログレベル。 | `"default"` | デバッグ時は `"all"` を推奨。 |
| `model` | 使用するAIモデルの指定。 | - | Claude 4.5系、Gemini 3 Pro、GPT-5系など。 |
| `parallel_tool_execution` | ツールの並列実行を有効にするか。 | `true` | - |
| `render_markdown` | ターミナル内でMarkdownをレンダリングするか。 | `true` | - |
| `screen_reader` | スクリーンリーダー用の最適化を有効にするか。 | `false` | - |
| `stream` | ストリーミングモードを有効にするか。 | `true` | - |
| `theme` | 出力のカラーテーマ。 | `"auto"` | `auto`, `dark`, `light` |
| `trusted_folders` | ファイル操作権限を付与するフォルダリスト。 | - | - |
| `undo_without_confirmation` | Esc 2回でのUndo時に確認をスキップするか。 | `false` | 実験的機能。`true`で即座に実行。 |
| `update_terminal_title` | ターミナルのタイトルを作業内容で更新するか。 | `true` | 対応するエミュレータ（iTerm, Windows Terminal等）が必要。 |

## Support Model

モデルの一覧を箇条書きのマークダウン形式でまとめました。

### **Anthropic (Claudeシリーズ)**

* `claude-sonnet-4.5`：デフォルト設定。速度と精度のバランスが取れた主力モデル。
* `claude-haiku-4.5`：軽量・高速。レスポンスの速さを重視する場合に最適。
* `claude-opus-4.5`：最高性能モデル。複雑なアルゴリズムの実装や設計判断に。
* `claude-sonnet-4`：安定性に定評のある前世代モデル。

### **OpenAI (GPTシリーズ)**

* `gpt-5.2`：最新の汎用フラグシップモデル。
* `gpt-5.2-codex`：最新のコード生成特化型モデル。
* `gpt-5.1` / `gpt-5.1-codex`：標準的なGPT-5系バリエーション。
* `gpt-5.1-codex-max`：大規模なコンテキスト処理に特化したCodex。
* `gpt-5.1-codex-mini` / `gpt-5-mini`：軽量版。簡単な修正や説明に。
* `gpt-5`：GPT-5系のベースモデル。
* `gpt-4.1`：軽量でリソース消費の少ない安定版。

### **Google (Geminiシリーズ)**

* `gemini-3-pro-preview`：非常に長いコンテキスト（長大なコードベース）の読み込みに強い。

## トラブルシューティング

ここからはよくあるトラブルシューティングをまとめていきます。

## Copilot CLIがインストールされていない場合

Copilot CLIがインストールされていない場合には以下のようなエラーが発生します。

```text
TypeError: unsupported operand type(s) for |: '_TypedDictMeta' and 'types.GenericAlias'
```

## 参考

- [cookbook](https://github.com/github/copilot-sdk/blob/main/cookbook/python/README.md)
- [GitHub Copilot CLI について](https://docs.github.com/ja/copilot/concepts/agents/about-copilot-cli)
- [GitHub Copilot SDKの発表](https://github.blog/jp/2026-01-23-build-an-agent-into-any-app-with-the-github-copilot-sdk/)
