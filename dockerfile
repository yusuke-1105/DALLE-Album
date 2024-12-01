FROM python:3.12-slim-bullseye

WORKDIR /app

# システム依存パッケージのインストール
RUN apt-get update
RUN apt-get install -y build-essential
RUN rm -rf /var/lib/apt/lists/*

# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir streamlit openai

# アプリケーションのポート設定
EXPOSE 8501

COPY DALLE-Album.py .
COPY images images

# 実行コマンド
CMD ["streamlit", "run", "DALLE-Album.py"]