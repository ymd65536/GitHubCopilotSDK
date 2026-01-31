# ベースイメージとして軽量なDebianを使用
FROM debian:bookworm-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLIのインストール
RUN type -p curl >/dev/null || (apt update && apt install curl -y)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt update \
    && apt install gh -y

# 作業用ユーザーの作成
RUN useradd -m -s /bin/bash developer
USER developer
WORKDIR /home/developer

# コンテナ起動後の使用方法:
# 1. gh auth login
# 2. gh extension install github/gh-copilot
# 3. gh copilot suggests "hello world"

CMD ["/bin/bash"]
