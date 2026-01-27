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
