# OpenTelemetryを使った可観測性

## Overview

GitHub Copilot CLIとOpenTelemetryを組み合わせて、アプリケーションの可観測性を向上させる方法について説明します。

## Observability Tools

- [OpenTelemetry](https://opentelemetry.io/)
- [Aspire](https://aspire.dev/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

## Aspire

`AspireHost/` に .NET Aspire AppHost を追加しています。.NET 10 SDK と、起動済みの Docker が必要です。リポジトリのルートから実行する場合:

```bash
dotnet run --project OpenTelemetry/AspireHost
```

すでに `OpenTelemetry/AspireHost` ディレクトリにいる場合は、次のように実行します。

```bash
dotnet run
```

Aspire Dashboard、OpenTelemetry Collector、Prometheus、Grafana をコンテナーとして起動します。Copilot CLI/SDK から送る OTLP は Collector が受信し、トレースとログを Aspire Dashboard へ、メトリクスを Aspire Dashboard と Prometheus へ転送します。設定ファイルは AppHost の出力先にコピーしてコンテナーへ読み取り専用でマウントするため、起動時の作業ディレクトリに依存しません。

`GF_SECURITY_ADMIN_PASSWORD` はローカル検証用の値です。共有環境では秘密情報に置き換えてください。また、匿名アクセスを有効にしている Aspire Dashboard は開発用ネットワークだけで使用してください。

## Prometheus

Collector は Prometheus exporter を `otel-collector:9464` で公開し、Prometheus が 15 秒ごとにメトリクスを scrape します。scrape の設定は [`prometheus.yml`](./prometheus.yml)、Collector の exporter 設定は [`otel-collector.yaml`](./otel-collector.yaml) を参照してください。

Prometheus の UI: <http://localhost:9090>。`up{job="otel-collector"}` を実行すると、Collector の exporter が scrape できているか確認できます。Copilot CLI/SDK のメトリクスを表示するには、下記の「起動と接続」にあるTelemetry設定を行ってください。

## Grafana

Grafana は起動時に Prometheus をデータソースとして登録します。設定は [`grafana-datasources.yaml`](./grafana-datasources.yaml) を参照してください。

Grafana: <http://localhost:3000>（ユーザー名 `admin`、パスワードは AppHost の `GF_SECURITY_ADMIN_PASSWORD`）

## 起動と接続

1. 上記いずれかの `dotnet run` コマンドでスタックを起動します。
2. Copilot CLI からCollectorへ送信する場合は、CLIを起動する前に次を設定します。

   ```bash
   export COPILOT_OTEL_ENABLED=true
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
   copilot
   ```

   `OTEL_EXPORTER_OTLP_ENDPOINT` はAspire AppHost内のDashboardではなく、OTLP/HTTPを受け付けるCollectorのURLです。SDKでは `TelemetryConfig` の OTLP endpoint に同じ `http://localhost:4318` を指定します。
3. Aspire Dashboard は <http://localhost:18880>、Prometheus は <http://localhost:9090>、Grafana は <http://localhost:3000> で開きます。Grafana のユーザー名は `admin`、初期パスワードは `change-me` です。

Prometheus が扱うのはメトリクスです。トレースやログは Aspire Dashboard で確認します。Grafana のトレース・ログ表示も必要な場合は、Tempo や Loki など対応するバックエンドを別途追加してください。

### Python SDKを使用する場合

Copilot CLIのTelemetryを送信するだけなら、以下のランタイムダウンロードは不要です。Python SDKを初めて使用する場合は、SDKの実行に必要なCopilot CLIランタイムを一度ダウンロードします。

```bash
python -m copilot download-runtime
```

## 参考

- [opentelemetry-monitoring](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#opentelemetry-monitoring)
- [OpenTelemetry instrumentation for Copilot SDK](https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry)
- [Aspire のコンテナーリソース API](https://aspire.dev/reference/api/csharp/aspire.hosting/containerresourcebuilderextensions/methods/)
- [Enterprise-managed OpenTelemetry export for VS Code and CLI](https://github.blog/changelog/2026-07-08-enterprise-managed-opentelemetry-export-for-vs-code-and-cli/)
- [Add Telemetry Endpoint Support](https://github.com/github/copilot-cli/issues/1565)
- [Managed telemetry.headers prevents OpenTelemetry (OTEL) export](https://github.com/github/copilot-cli/issues/4669)
- [Feature Request: Enterprise OTel auth — mTLS env vars + dynamic-headers helper (parity with Claude Code)](https://github.com/github/copilot-cli/issues/3477)
- [Dynamic workflows in Copilot CLI and the Copilot app](https://github.blog/changelog/2026-10-01-dynamic-workflows-in-copilot-cli-and-the-copilot-app/)
