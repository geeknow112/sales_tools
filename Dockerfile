FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージの更新とインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ .

# ポート8080を公開
EXPOSE 8080

# ヘルスチェック用エンドポイント
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# アプリケーションの起動
CMD ["python", "app.py"]
