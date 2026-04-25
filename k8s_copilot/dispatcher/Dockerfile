FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dispatcherスクリプトのコピー
COPY dispatcher.py .

# ポート公開
EXPOSE 8000

# Dispatcherの実行
CMD ["python", "dispatcher.py"]
