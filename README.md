# 📖 概要
このリポジトリは、Streamlitを使用してアルバムジャケットを生成するアプリケーション「DALLE-DJ」を提供します。ユーザーはプロンプトを入力し、スタイルタグを選択することで、OpenAIのAPIを使用してアルバムジャケットを生成できます。

# 🛠 必要なツール、ライブラリ
このアプリケーションを実行するために必要なツールとライブラリは以下の通りです：

- Python 3.12
- Streamlit
- OpenAI

これらの依存関係は、`requirements.txt`ファイルにリストされています。

# 🚀 使い方
1. リポジトリをクローンします：
    ```sh
    git clone <リポジトリのURL>
    cd <リポジトリのディレクトリ>
    ```

2. Dockerを使用してアプリケーションをビルドし、実行します：
    ```sh
    docker build -t dalle-album .
    docker run -p 8501:8501 dalle-album
    ```
    ※Dockerを使用できない場合は、以下のコマンドを実行する
    ```python
    streamlit run DALLE-Album.py
    ```
    なお、`--server.address localhost`オプションを追加することで、アプリケーションをローカルホストでのみ実行できます。

3. ブラウザで `http://localhost:8501` にアクセスし、アプリケーションを使用します。

アプリケーションの設定画面でAPIキーを入力し、プロンプトとスタイルタグを選択してアルバムジャケットを生成します。