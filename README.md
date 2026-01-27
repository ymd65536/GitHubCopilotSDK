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
