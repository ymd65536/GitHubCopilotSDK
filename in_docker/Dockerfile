# ベースイメージとして軽量なDebianを使用
FROM debian:bookworm-slim

# 必要なパッケージとGitHub CLIのインストールを1つのレイヤーに統合
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    nodejs \
    npm \
    ca-certificates \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && npm install -g @github/copilot \
    && npm cache clean --force \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 作業用ユーザーの作成
RUN useradd -m -s /bin/bash developer
USER developer
WORKDIR /home/developer

# ポート4321を公開
EXPOSE 4321

# Copilotサーバーをポート4321で起動（外部アクセス可能にするため0.0.0.0でリッスン）
CMD ["copilot", "--server", "--port", "4321"]
