# テレアポ文字起こしシステム MVP

## 概要
このシステムは、テレアポの音声ファイルを自動で文字起こしし、Google Sheetsに結果を保存するMVP（Minimum Viable Product）です。

## 機能
- mp3形式の音声ファイルをアップロード（最大25MB）
- OpenAI Whisper APIを使用した音声の文字起こし
- 文字起こし結果をGoogle Sheetsに自動保存

## 必要条件
- Python 3.11以上
- OpenAI APIキー
- Google Sheets APIの認証情報

## セットアップ方法

1. リポジトリをクローン
```
git clone [リポジトリURL]
cd teleapo_mvp
```

2. 仮想環境を作成・有効化
```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存パッケージをインストール
```
pip install -r requirements.txt
```

4. 環境変数の設定
- `.env.example` ファイルを `.env` にコピーし、実際のAPIキーを設定
```
cp .env.example .env
# .envファイルを編集して実際のAPIキーを設定
```

5. Google Sheets APIの認証設定
- Google Cloud Consoleでプロジェクトを作成
- Sheets API と Drive API を有効化
- サービスアカウントを作成し、credentials.jsonをダウンロード
- `credentials.json.example` ファイルを参考に、ダウンロードした認証情報を `credentials.json` として保存
```
cp credentials.json.example credentials.json
# credentials.jsonを実際のファイルで置き換え
```
- スプレッドシート「テレアポチェックシート」を作成し、サービスアカウントと共有

## セキュリティに関する注意
- `.env` ファイルと `credentials.json` はGitにコミットしないでください（.gitignoreに追加済み）
- APIキーやサービスアカウント認証情報は機密情報として安全に管理してください
- 認証情報ファイルには適切なアクセス権限を設定することを推奨します:
```
chmod 600 credentials.json
```

## 使用方法
1. アプリケーションを起動
```
streamlit run app.py
```

2. ブラウザで表示されるUIでmp3ファイルをアップロード
3. 「文字起こし開始」ボタンをクリック
4. 処理が完了すると、結果が画面に表示され、Google Sheetsに保存されます 

# ファイルの権限を確認
ls -la /Users/kohteddy/Desktop/SFIDA\ X/project2/teleapo_mvp/credentials.json

# 必要に応じて権限を変更
chmod 600 /Users/kohteddy/Desktop/SFIDA\ X/project2/teleapo_mvp/credentials.json 